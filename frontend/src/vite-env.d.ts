/// <reference types="vite/client" />

// Extend Vite's built-in environment types
declare module 'vite/client' {
  interface ImportMetaEnv {
    readonly DEV: boolean
    readonly PROD: boolean
    readonly MODE: string
    // Add other env variables as needed
  }
}
