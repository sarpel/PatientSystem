-- Clinical AI Assistant - Database Initialization Script
-- Creates database, user, and initial schema for Clinical AI system

-- Enable SQLCMD mode
:on error exit

-- Print separator for better logging
PRINT N'=================================================='
PRINT N'Clinical AI Assistant - Database Initialization'
PRINT N'Started at: ' + CONVERT(nvarchar, GETDATE())
PRINT N'=================================================='
PRINT N''

-- Create ClinicalAI database if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'ClinicalAI')
BEGIN
    PRINT N'Creating ClinicalAI database...'

    CREATE DATABASE ClinicalAI
    COLLATE Turkish_CI_AS;

    PRINT N'ClinicalAI database created successfully.'
END
ELSE
BEGIN
    PRINT N'ClinicalAI database already exists.'
END

PRINT N''

-- Use the ClinicalAI database
USE ClinicalAI;
GO

-- Create clinicalai_user if it doesn't exist
IF NOT EXISTS (SELECT name FROM sys.database_principals WHERE name = 'clinicalai_user')
BEGIN
    PRINT N'Creating clinicalai_user...'

    CREATE USER clinicalai_user FOR LOGIN clinicalai_user
    WITH DEFAULT_SCHEMA = dbo;

    -- Grant necessary permissions
    ALTER ROLE db_datareader ADD MEMBER clinicalai_user;
    ALTER ROLE db_datawriter ADD MEMBER clinicalai_user;
    ALTER ROLE db_ddladmin ADD MEMBER clinicalai_user;

    PRINT N'clinicalai_user created and permissions granted.'
END
ELSE
BEGIN
    PRINT N'clinicalai_user already exists.'
END

PRINT N''

-- Create schema objects
PRINT N'Creating database schema objects...'

-- Create custom data types for medical data
IF NOT EXISTS (SELECT * FROM sys.types WHERE name = 'TCKN' AND is_table_type = 0)
BEGIN
    EXEC sp_addtype N'TCKN', N'varchar(11)', N'NOT NULL';
    PRINT N'Created TCKN data type.'
END

IF NOT EXISTS (SELECT * FROM sys.types WHERE name = 'MoneyAmount' AND is_table_type = 0)
BEGIN
    EXEC sp_addtype N'MoneyAmount', N'decimal(18,2)', N'NULL';
    PRINT N'Created MoneyAmount data type.'
END

-- Create essential tables for Clinical AI Assistant

-- Patients table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'HASTA')
BEGIN
    CREATE TABLE HASTA (
        TCKN TCKN PRIMARY KEY,
        ADI varchar(50) NOT NULL,
        SOYADI varchar(50) NOT NULL,
        DOGUM_TARIHI date NOT NULL,
        CINSIYET char(1) CHECK (CINSIYET IN ('E', 'K', 'U')),
        TELEFON varchar(20),
        ADRES varchar(500),
        EMAIL varchar(100),
        KAYIT_TARIHI datetime DEFAULT GETDATE(),
        GUNCELLEME_TARIHI datetime DEFAULT GETDATE(),
        AKTIF bit DEFAULT 1
    );

    CREATE INDEX IX_HASTA_ADI_SOYADI ON HASTA(ADI, SOYADI);
    CREATE INDEX IX_HASTA_DOGUM_TARIHI ON HASTA(DOGUM_TARIHI);
    CREATE INDEX IX_HASTA_AKTIF ON HASTA(AKTIF);

    PRINT N'Created HASTA (Patients) table.'
END

-- Visits table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'MUAYENE')
BEGIN
    CREATE TABLE MUAYENE (
        MUAYENE_ID int IDENTITY(1,1) PRIMARY KEY,
        TCKN TCKN NOT NULL,
        MUAYENE_TARIHI datetime NOT NULL DEFAULT GETDATE(),
        DOKTOR_ID int NOT NULL,
        SIKAYET varchar(1000),
        TANI varchar(500),
        TEDAVI varchar(1000),
        LAB_TETKIKLERI varchar(500),
        RECETE varchar(500),
        KONTROL_TARIHI datetime,
        DURUM varchar(50) DEFAULT 'Aktif',
        NOTLAR varchar(2000),
        KAYIT_ZAMANI datetime DEFAULT GETDATE(),
        FOREIGN KEY (TCKN) REFERENCES HASTA(TCKN)
    );

    CREATE INDEX IX_MUAYENE_TCKN_TARIH ON MUAYENE(TCKN, MUAYENE_TARIHI);
    CREATE INDEX IX_MUAYENE_DOKTOR_TARIH ON MUAYENE(DOKTOR_ID, MUAYENE_TARIHI);
    CREATE INDEX IX_MUAYENE_DURUM ON MUAYENE(DURUM);

    PRINT N'Created MUAYENE (Visits) table.'
END

-- Laboratory Results table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'LAB_SONUCLARI')
BEGIN
    CREATE TABLE LAB_SONUCLARI (
        LAB_ID int IDENTITY(1,1) PRIMARY KEY,
        TCKN TCKN NOT NULL,
        TEST_ADI varchar(100) NOT NULL,
        SONUC varchar(100) NOT NULL,
        BIRIM varchar(20),
        NORMAL_MIN varchar(20),
        NORMAL_MAX varchar(20),
        TEST_TARIHI datetime NOT NULL DEFAULT GETDATE(),
        LAB_TEKNISYENI varchar(100),
        ONAYLI bit DEFAULT 0,
        NOTLAR varchar(500),
        FOREIGN KEY (TCKN) REFERENCES HASTA(TCKN)
    );

    CREATE INDEX IX_LAB_TCKN_TEST_TARIH ON LAB_SONUCLARI(TCKN, TEST_TARIHI);
    CREATE INDEX IX_LAB_TEST_ADI ON LAB_SONUCLARI(TEST_ADI);
    CREATE INDEX IX_LAB_TEST_TARIHI ON LAB_SONUCLARI(TEST_TARIHI);

    PRINT N'Created LAB_SONUCLARI (Laboratory Results) table.'
END

-- Prescriptions table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'RECETELER')
BEGIN
    CREATE TABLE RECETELER (
        RECETE_ID int IDENTITY(1,1) PRIMARY KEY,
        TCKN TCKN NOT NULL,
        RECETE_TARIHI datetime NOT NULL DEFAULT GETDATE(),
        DOKTOR_ID int NOT NULL,
        HASTA_YASI int,
        KRONIK bit DEFAULT 0,
        TESHIS_KODU varchar(10),
        PROTOKOL_NO varchar(20),
        DURUM varchar(20) DEFAULT 'Aktif',
        ILAC_LISTESI varchar(2000),
        KULLANIM_TALIMATI varchar(1000),
        NOTLAR varchar(1000),
        FOREIGN KEY (TCKN) REFERENCES HASTA(TCKN)
    );

    CREATE INDEX IX_RECETE_TCKN_TARIH ON RECETELER(TCKN, RECETE_TARIHI);
    CREATE INDEX IX_RECETE_DOKTOR_TARIH ON RECETELER(DOKTOR_ID, RECETE_TARIHI);
    CREATE INDEX IX_RECETE_DURUM ON RECETELER(DURUM);

    PRINT N'Created RECETELER (Prescriptions) table.'
END

-- AI Analysis Results table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'AI_ANALIZLERI')
BEGIN
    CREATE TABLE AI_ANALIZLERI (
        ANALIZ_ID int IDENTITY(1,1) PRIMARY KEY,
        TCKN TCKN NOT NULL,
        ANALIZ_TIPI varchar(50) NOT NULL, -- 'DIAGNOSIS', 'TREATMENT', 'DRUG_INTERACTION'
        GIRDI_VERISI varchar(2000) NOT NULL,
        AI_MODELI varchar(50) NOT NULL,
        CIKTI_VERISI varchar(5000),
        GUVENILIK_SKORU decimal(3,2), -- Confidence score 0-1
        ANALIZ_SURESI int, -- Analysis duration in seconds
        OLUSTURMA_TARIHI datetime DEFAULT GETDATE(),
        KULLANICI_ID int,
        ONAYLANDI bit DEFAULT 0,
        NOTLAR varchar(1000),
        FOREIGN KEY (TCKN) REFERENCES HASTA(TCKN)
    );

    CREATE INDEX IX_AI_ANALIZ_TCKN_TIPI ON AI_ANALIZLERI(TCKN, ANALIZ_TIPI);
    CREATE INDEX IX_AI_ANALIZ_TARIH ON AI_ANALIZLERI(OLUSTURMA_TARIHI);
    CREATE INDEX IX_AI_ANALIZ_MODELI ON AI_ANALIZLERI(AI_MODELI);

    PRINT N'Created AI_ANALIZLERI (AI Analysis Results) table.'
END

-- Drug Interactions table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'ILAC_ETKILESIMLERI')
BEGIN
    CREATE TABLE ILAC_ETKILESIMLERI (
        ETKILESIM_ID int IDENTITY(1,1) PRIMARY KEY,
        ILAC1 varchar(100) NOT NULL,
        ILAC2 varchar(100) NOT NULL,
        ETKILESIM_TIPI varchar(50) NOT NULL, -- 'PHARMACODYNAMIC', 'PHARMACOKINETIC', etc.
    SEVIYE varchar(20) NOT NULL, -- 'CRITICAL', 'MAJOR', 'MODERATE', 'MINOR'
    ETKI varchar(500),
    YONTEMLER varchar(1000),
    ALTERNATIF_ILACLAR varchar(500),
        OLUSTURMA_TARIHI datetime DEFAULT GETDATE(),
        KAYNAK varchar(100), -- Source of interaction data
        GUNCELLEME_TARIHI datetime DEFAULT GETDATE()
    );

    CREATE INDEX IX_ETKILESIM_ILACLAR ON ILAC_ETKILESIMLERI(ILAC1, ILAC2);
    CREATE INDEX IX_ETKILESIM_SEVIYE ON ILAC_ETKILESIMLERI(SEVIYE);

    PRINT N'Created ILAC_ETKILESIMLERI (Drug Interactions) table.'
END

-- System Configuration table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'SISTEM_AYARLARI')
BEGIN
    CREATE TABLE SISTEM_AYARLARI (
        AYAR_ID int IDENTITY(1,1) PRIMARY KEY,
        AYAR_AD varchar(100) NOT NULL UNIQUE,
        AYAR_DEGER varchar(1000),
        AYAR_TIPI varchar(20) DEFAULT 'STRING', -- 'STRING', 'INTEGER', 'BOOLEAN', 'JSON'
        TANIM varchar(500),
        OLUSTURMA_TARIHI datetime DEFAULT GETDATE(),
        GUNCELLEME_TARIHI datetime DEFAULT GETDATE(),
        GUNCELLEYEN varchar(50)
    );

    -- Insert default system settings
    INSERT INTO SISTEM_AYARLARI (AYAR_AD, AYAR_DEGER, AYAR_TIPI, TANIM) VALUES
    ('AI_DEFAULT_MODEL', 'gemma:7b', 'STRING', 'Default AI model for analysis'),
    ('AI_TIMEOUT', '30', 'INTEGER', 'AI request timeout in seconds'),
    ('AI_TEMPERATURE', '0.7', 'STRING', 'AI sampling temperature'),
    ('MAX_ANALYSIS_HISTORY', '100', 'INTEGER', 'Maximum number of analysis results to keep per patient'),
    ('AUTO_SAVE_ENABLED', 'true', 'BOOLEAN', 'Enable automatic saving of AI analysis results'),
    ('DATA_RETENTION_MONTHS', '84', 'INTEGER', 'Data retention period in months (7 years)'),
    ('ENABLE_AUDIT_LOG', 'true', 'BOOLEAN', 'Enable audit logging'),
    ('SECURITY_KEY_ROTATION_MONTHS', '6', 'INTEGER', 'Security key rotation period in months'),
    ('BACKUP_SCHEDULE', '0 2 * * *', 'STRING', 'Backup schedule in cron format'),
    ('MONITORING_ENABLED', 'true', 'BOOLEAN', 'Enable system monitoring');

    PRINT N'Created SISTEM_AYARLARI (System Configuration) table with default settings.'
END

-- Audit Log table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'DENETIM_LOGU')
BEGIN
    CREATE TABLE DENETIM_LOGU (
        LOG_ID int IDENTITY(1,1) PRIMARY KEY,
        KULLANICI_ID int,
        TCKN TCKN,
        ISLEM varchar(100) NOT NULL, -- Operation performed
        TABLO_AD varchar(50), -- Table affected
        KAYIT_ID int, -- Record ID affected
        ESKI_DEGER varchar(2000), -- Old value (for updates)
        YENI_DEGER varchar(2000), -- New value
        IP_ADRES varchar(45),
        KULLANICI_ARACI varchar(200),
        ISLEM_ZAMANI datetime DEFAULT GETDATE(),
        BASARILI bit DEFAULT 1,
        HATA_MESAJI varchar(1000)
    );

    CREATE INDEX IX_DENETIM_KULLANICI ON DENETIM_LOGU(KULLANICI_ID);
    CREATE INDEX IX_DENETIM_TCKN ON DENETIM_LOGU(TCKN);
    CREATE INDEX IX_DENETIM_ISLEM ON DENETIM_LOGU(ISLEM);
    CREATE INDEX IX_DENETIM_ZAMAN ON DENETIM_LOGU(ISLEM_ZAMANI);

    PRINT N'Created DENETIM_LOGU (Audit Log) table.'
END

PRINT N''

-- Create stored procedures for common operations

-- Procedure to get patient summary
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_HastaOzetGetir')
BEGIN
    DROP PROCEDURE sp_HastaOzetGetir;
END

CREATE PROCEDURE sp_HastaOzetGetir
    @TCKN TCKN
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        h.TCKN,
        h.ADI + ' ' + h.SOYADI AS AD_SOYAD,
        h.DOGUM_TARIHI,
        DATEDIFF(YEAR, h.DOGUM_TARIHI, GETDATE()) AS YAS,
        h.CINSIYET,
        h.TELEFON,
        h.ADRES,
        h.EMAIL,
        COUNT(DISTINCT m.MUAYENE_ID) AS TOPLAM_MUAYENE,
        MAX(m.MUAYENE_TARIHI) AS SON_MUAYENE_TARIHI,
        COUNT(DISTINCT l.LAB_ID) AS TOPLAM_LAB_TESTI,
        COUNT(DISTINCT r.RECETE_ID) AS TOPLAM_RECETE
    FROM HASTA h
    LEFT JOIN MUAYENE m ON h.TCKN = m.TCKN
    LEFT JOIN LAB_SONUCLARI l ON h.TCKN = l.TCKN
    LEFT JOIN RECETELER r ON h.TCKN = r.TCKN
    WHERE h.TCKN = @TCKN AND h.AKTIF = 1
    GROUP BY h.TCKN, h.ADI, h.SOYADI, h.DOGUM_TARIHI, h.CINSIYET, h.TELEFON, h.ADRES, h.EMAIL;
END;

PRINT N'Created sp_HastaOzetGetir stored procedure.'

-- Procedure to save AI analysis
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_AIAnalizKaydet')
BEGIN
    DROP PROCEDURE sp_AIAnalizKaydet;
END

CREATE PROCEDURE sp_AIAnalizKaydet
    @TCKN TCKN,
    @AnalizTipi varchar(50),
    @GirdiVerisi varchar(2000),
    @AIModeli varchar(50),
    @CiktiVerisi varchar(5000),
    @GuvvenilikSkoru decimal(3,2) = NULL,
    @AnalizSuresi int = NULL,
    @KullaniciID int = NULL,
    @Notlar varchar(1000) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO AI_ANALIZLERI (
        TCKN, ANALIZ_TIPI, GIRDI_VERISI, AI_MODELI,
        CIKTI_VERISI, GUVENILIK_SKORU, ANALIZ_SURESI,
        KULLANICI_ID, NOTLAR
    )
    VALUES (
        @TCKN, @AnalizTipi, @GirdiVerisi, @AIModeli,
        @CiktiVerisi, @GuvvenilikSkoru, @AnalizSuresi,
        @KullaniciID, @Notlar
    );

    SELECT SCOPE_IDENTITY() AS YeniAnalizID;
END;

PRINT N'Created sp_AIAnalizKaydet stored procedure.'

-- Procedure to get drug interactions
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'sp_IlacEtkilesimleriGetir')
BEGIN
    DROP PROCEDURE sp_IlacEtkilesimleriGetir;
END

CREATE PROCEDURE sp_IlacEtkilesimleriGetir
    @IlacAdi varchar(100),
    @Seviye varchar(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        ETKILESIM_ID,
        ILAC1,
        ILAC2,
        ETKILESIM_TIPI,
        SEVIYE,
        ETKI,
        YONTEMLER,
        ALTERNATIF_ILACLAR,
        KAYNAK
    FROM ILAC_ETKILESIMLERI
    WHERE (ILAC1 = @IlacAdi OR ILAC2 = @IlacAdi)
    AND (@Seviye IS NULL OR SEVIYE = @Seviye)
    ORDER BY
        CASE SEVIYE
            WHEN 'CRITICAL' THEN 1
            WHEN 'MAJOR' THEN 2
            WHEN 'MODERATE' THEN 3
            WHEN 'MINOR' THEN 4
        END;
END;

PRINT N'Created sp_IlacEtkilesimleriGetir stored procedure.'

PRINT N''
PRINT N'=================================================='
PRINT N'Database initialization completed successfully!'
PRINT N'Completed at: ' + CONVERT(nvarchar, GETDATE())
PRINT N'=================================================='