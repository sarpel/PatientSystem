"""Performance benchmarks for Clinical AI Assistant."""

import asyncio
import statistics
import time
from typing import Dict, List
from unittest.mock import AsyncMock, patch

import pytest

from src.ai.router import AIRouter
from src.clinical.diagnosis_engine import DiagnosisEngine
from src.clinical.treatment_engine import TreatmentEngine
from src.database.connection import get_engine, get_session


@pytest.mark.performance
class TestAIBenchmarks:
    """Performance benchmarks for AI operations."""

    @pytest.mark.asyncio
    async def test_diagnosis_generation_performance(self, performance_thresholds):
        """Benchmark diagnosis generation performance."""
        router = AIRouter()

        # Mock AI clients for consistent timing
        mock_claude = AsyncMock()
        mock_claude.return_value = {
            "text": '{"differential_diagnosis": [{"diagnosis": "Test", "probability": 0.8}]}',
            "model": "claude-3-5-sonnet",
            "provider": "claude",
        }

        with patch(
            "src.ai.router.AIRouter.route_and_complete", return_value=mock_claude.return_value
        ):
            diagnosis_engine = DiagnosisEngine()

            # Run multiple iterations
            timings = []
            iterations = 10

            for i in range(iterations):
                start_time = time.time()

                result = await diagnosis_engine.generate_differential_diagnosis_ai(
                    tckn="12345678901",
                    chief_complaint=f"Test patient complaint {i}",
                    preferred_provider="claude",
                )

                end_time = time.time()
                timings.append(end_time - start_time)

                # Verify result is valid
                assert "differential_diagnosis" in result

        # Calculate statistics
        avg_time = statistics.mean(timings)
        max_time = max(timings)
        min_time = min(timings)

        # Performance assertions
        assert (
            avg_time < performance_thresholds["diagnosis_generation_seconds"]
        ), f"Average diagnosis time {avg_time:.2f}s exceeds threshold {performance_thresholds['diagnosis_generation_seconds']}s"

        assert (
            max_time < performance_thresholds["diagnosis_generation_seconds"] * 2
        ), f"Maximum diagnosis time {max_time:.2f}s exceeds 2x threshold"

        print(f"Diagnosis Generation Performance:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")
        print(f"  Iterations: {iterations}")

    @pytest.mark.asyncio
    async def test_treatment_generation_performance(self, performance_thresholds):
        """Benchmark treatment generation performance."""
        with patch("src.ai.router.AIRouter.route_and_complete") as mock_ai:
            mock_ai.return_value = {
                "text": '{"medications": [{"name": "Test Medication"}]}',
                "model": "claude-3-5-sonnet",
                "provider": "claude",
            }

            treatment_engine = TreatmentEngine()

            # Run multiple iterations
            timings = []
            iterations = 10

            for i in range(iterations):
                start_time = time.time()

                result = await treatment_engine.suggest_treatment_ai(
                    tckn="12345678901", diagnosis=f"Test Diagnosis {i}", preferred_provider="claude"
                )

                end_time = time.time()
                timings.append(end_time - start_time)

                # Verify result is valid
                assert "medications" in result

        # Calculate statistics
        avg_time = statistics.mean(timings)
        max_time = max(timings)
        min_time = min(timings)

        # Performance assertions
        assert (
            avg_time < performance_thresholds["diagnosis_generation_seconds"]
        ), f"Average treatment time {avg_time:.2f}s exceeds threshold {performance_thresholds['diagnosis_generation_seconds']}s"

        print(f"Treatment Generation Performance:")
        print(f"  Average: {avg_time:.2f}s")
        print(f"  Min: {min_time:.2f}s")
        print(f"  Max: {max_time:.2f}s")
        print(f"  Iterations: {iterations}")

    @pytest.mark.asyncio
    async def test_concurrent_ai_requests(self, performance_thresholds):
        """Benchmark concurrent AI request handling."""
        with patch("src.ai.router.AIRouter.route_and_complete") as mock_ai:
            mock_ai.return_value = {
                "text": '{"diagnosis": "Test"}',
                "model": "claude-3-5-sonnet",
                "provider": "claude",
            }

            diagnosis_engine = DiagnosisEngine()

            # Create concurrent requests
            num_requests = 10
            start_time = time.time()

            tasks = [
                diagnosis_engine.generate_differential_diagnosis_ai(
                    tckn=f"1234567890{i:02d}",
                    chief_complaint=f"Test complaint {i}",
                    preferred_provider="claude",
                )
                for i in range(num_requests)
            ]

            results = await asyncio.gather(*tasks)
            end_time = time.time()

            total_time = end_time - start_time
            avg_per_request = total_time / num_requests

            # Performance assertions
            assert (
                avg_per_request < performance_thresholds["diagnosis_generation_seconds"]
            ), f"Average concurrent time {avg_per_request:.2f}s exceeds threshold"

            assert (
                total_time < performance_thresholds["diagnosis_generation_seconds"] * 3
            ), f"Total concurrent time {total_time:.2f}s exceeds 3x threshold"

            # Verify all requests succeeded
            assert len(results) == num_requests
            for result in results:
                assert "differential_diagnosis" in result

            print(f"Concurrent AI Requests Performance:")
            print(f"  Total requests: {num_requests}")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Average per request: {avg_per_request:.2f}s")
            print(f"  Requests per second: {num_requests/total_time:.2f}")


@pytest.mark.performance
@pytest.mark.database
class TestDatabaseBenchmarks:
    """Performance benchmarks for database operations."""

    def test_patient_search_performance(self, performance_thresholds):
        """Benchmark patient search performance."""
        with get_session() as session:
            # Mock a large dataset for testing
            search_terms = ["Test", "Patient", "Smith", "John", "Ahmet", "Mehmet"]

            timings = []

            for term in search_terms:
                start_time = time.time()

                # Simulate patient search query
                query = session.execute(
                    "SELECT COUNT(*) FROM HASTA WHERE ADI LIKE :term OR SOYADI LIKE :term",
                    {"term": f"%{term}%"},
                )

                end_time = time.time()
                timings.append(end_time - start_time)

            avg_time = statistics.mean(timings)
            max_time = max(timings)

            # Performance assertions
            assert (
                avg_time < performance_thresholds["database_query_ms"] / 1000
            ), f"Average search time {avg_time:.3f}s exceeds threshold {performance_thresholds['database_query_ms']/1000}s"

            print(f"Patient Search Performance:")
            print(f"  Average: {avg_time:.3f}s")
            print(f"  Max: {max_time:.3f}s")
            print(f"  Searches: {len(search_terms)}")

    def test_lab_data_retrieval_performance(self, performance_thresholds):
        """Benchmark lab data retrieval performance."""
        with get_session() as session:
            test_tckns = ["12345678901", "12345678902", "12345678903"]

            timings = []

            for tckn in test_tckns:
                start_time = time.time()

                # Simulate lab data query
                query = session.execute(
                    "SELECT COUNT(*) FROM TETKIK WHERE TCKN = :tckn", {"tckn": tckn}
                )

                end_time = time.time()
                timings.append(end_time - start_time)

            avg_time = statistics.mean(timings)

            # Performance assertions
            assert (
                avg_time < performance_thresholds["database_query_ms"] / 1000
            ), f"Average lab query time {avg_time:.3f}s exceeds threshold"

            print(f"Lab Data Retrieval Performance:")
            print(f"  Average: {avg_time:.3f}s")
            print(f"  Queries: {len(test_tckns)}")


@pytest.mark.performance
class TestAPIBenchmarks:
    """Performance benchmarks for API endpoints."""

    def test_api_response_times(self, test_client, performance_thresholds):
        """Benchmark API endpoint response times."""
        endpoints = [
            ("/health", "GET"),
            ("/health/database", "GET"),
        ]

        for endpoint, method in endpoints:
            timings = []
            iterations = 5

            for _ in range(iterations):
                start_time = time.time()

                if method == "GET":
                    response = test_client.get(endpoint)

                end_time = time.time()
                timings.append((end_time - start_time) * 1000)  # Convert to ms

                # Verify response is successful
                assert response.status_code in [200, 404]  # 404 is acceptable for some endpoints

            avg_time = statistics.mean(timings)
            max_time = max(timings)

            # Performance assertions
            assert (
                avg_time < performance_thresholds["api_response_ms"]
            ), f"API {endpoint} average time {avg_time:.0f}ms exceeds threshold {performance_thresholds['api_response_ms']}ms"

            print(f"API Endpoint {endpoint} Performance:")
            print(f"  Average: {avg_time:.0f}ms")
            print(f"  Max: {max_time:.0f}ms")
            print(f"  Iterations: {iterations}")

    def test_concurrent_api_requests(self, test_client, performance_thresholds):
        """Benchmark concurrent API request handling."""
        import threading
        from queue import Queue

        def make_request(queue, endpoint):
            """Make API request and return timing."""
            start_time = time.time()
            response = test_client.get(endpoint)
            end_time = time.time()
            queue.put((end_time - start_time) * 1000)  # Convert to ms

        # Test concurrent requests to health endpoint
        num_requests = 10
        threads = []
        results_queue = Queue()

        start_time = time.time()

        # Create and start threads
        for _ in range(num_requests):
            thread = threading.Thread(target=make_request, args=(results_queue, "/health"))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        total_time = end_time - start_time

        # Collect results
        timings = []
        while not results_queue.empty():
            timings.append(results_queue.get())

        avg_time = statistics.mean(timings)
        requests_per_second = num_requests / total_time

        # Performance assertions
        assert (
            avg_time < performance_thresholds["api_response_ms"] * 2
        ), f"Concurrent API average time {avg_time:.0f}ms exceeds 2x threshold"

        print(f"Concurrent API Requests Performance:")
        print(f"  Total requests: {num_requests}")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Requests per second: {requests_per_second:.1f}")
        print(f"  Average response time: {avg_time:.0f}ms")


@pytest.mark.performance
class TestSystemBenchmarks:
    """Overall system performance benchmarks."""

    @pytest.mark.asyncio
    async def test_full_workflow_performance(self, performance_thresholds):
        """Benchmark complete clinical workflow performance."""
        with patch("src.ai.router.AIRouter.route_and_complete") as mock_ai:
            mock_ai.return_value = {
                "text": '{"diagnosis": "Test", "medications": []}',
                "model": "claude-3-5-sonnet",
                "provider": "claude",
            }

            # Start timing
            start_time = time.time()

            # Step 1: Generate diagnosis
            diagnosis_engine = DiagnosisEngine()
            diagnosis_result = await diagnosis_engine.generate_differential_diagnosis_ai(
                tckn="12345678901",
                chief_complaint="Test complaint for performance testing",
                preferred_provider="claude",
            )

            # Step 2: Generate treatment
            treatment_engine = TreatmentEngine()
            treatment_result = await treatment_engine.suggest_treatment_ai(
                tckn="12345678901", diagnosis="Test Diagnosis", preferred_provider="claude"
            )

            end_time = time.time()
            total_time = end_time - start_time

            # Performance assertions
            assert (
                total_time < performance_thresholds["diagnosis_generation_seconds"] * 3
            ), f"Full workflow time {total_time:.2f}s exceeds 3x threshold"

            print(f"Full Workflow Performance:")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Diagnosis generated: {'Yes' if diagnosis_result else 'No'}")
            print(f"  Treatment generated: {'Yes' if treatment_result else 'No'}")

    def test_memory_usage_simulation(self):
        """Simulate memory usage patterns."""
        import os

        import psutil

        # Get current process
        process = psutil.Process(os.getpid())

        # Initial memory usage
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Simulate processing multiple patients
        patient_data = []
        for i in range(100):
            patient_data.append(
                {
                    "tckn": f"1234567890{i:03d}",
                    "name": f"Test Patient {i}",
                    "complaint": f"Test complaint {i}",
                    "data": "x" * 1000,  # Simulate 1KB of data per patient
                }
            )

        # Memory after processing
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory

        # Clean up
        del patient_data

        print(f"Memory Usage Simulation:")
        print(f"  Initial memory: {initial_memory:.1f} MB")
        print(f"  Peak memory: {peak_memory:.1f} MB")
        print(f"  Memory increase: {memory_increase:.1f} MB")
        print(f"  Memory per patient: {memory_increase/100:.2f} MB")

        # Memory usage should be reasonable (less than 100MB for 100 patients)
        assert (
            memory_increase < 100
        ), f"Memory increase {memory_increase:.1f}MB exceeds reasonable threshold"


@pytest.mark.performance
class TestScalabilityBenchmarks:
    """Scalability and load testing benchmarks."""

    @pytest.mark.asyncio
    async def test_scalability_with_increasing_load(self):
        """Test system scalability with increasing load."""
        with patch("src.ai.router.AIRouter.route_and_complete") as mock_ai:
            mock_ai.return_value = {
                "text": '{"diagnosis": "Test"}',
                "model": "claude-3-5-sonnet",
                "provider": "claude",
            }

            diagnosis_engine = DiagnosisEngine()

            # Test with increasing number of concurrent requests
            load_levels = [1, 5, 10, 20]
            results = {}

            for load in load_levels:
                start_time = time.time()

                tasks = [
                    diagnosis_engine.generate_differential_diagnosis_ai(
                        tckn=f"1234567890{i:03d}",
                        chief_complaint=f"Test complaint {i}",
                        preferred_provider="claude",
                    )
                    for i in range(load)
                ]

                await asyncio.gather(*tasks)
                end_time = time.time()

                total_time = end_time - start_time
                throughput = load / total_time

                results[load] = {"total_time": total_time, "throughput": throughput}

                print(f"Load Level {load}:")
                print(f"  Total time: {total_time:.2f}s")
                print(f"  Throughput: {throughput:.1f} requests/second")

            # Verify scalability doesn't degrade significantly
            if len(results) > 1:
                first_throughput = list(results.values())[0]["throughput"]
                last_throughput = list(results.values())[-1]["throughput"]
                degradation_ratio = last_throughput / first_throughput

                assert (
                    degradation_ratio > 0.5
                ), f"Throughput degradation too severe: {degradation_ratio:.2f}"

                print(f"Scalability Results:")
                print(f"  Throughput ratio (max/min): {degradation_ratio:.2f}")
                print(
                    f"  Scalability: {'Good' if degradation_ratio > 0.7 else 'Fair' if degradation_ratio > 0.5 else 'Poor'}"
                )
