const nextJest = require('next/jest')

// Create Jest config with Next.js support
const createJestConfig = nextJest({
  // Provide path to Next.js app
  dir: './',
})

// Custom Jest configuration
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/__tests__/setup.ts'],
  testEnvironment: 'jest-environment-jsdom',
  moduleNameMapper: {
    // Handle module aliases (from tsconfig.json)
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testMatch: [
    '**/__tests__/**/*.test.ts',
    '**/__tests__/**/*.test.tsx',
  ],
  collectCoverageFrom: [
    'src/**/*.{ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.tsx',
    '!src/components/ui/**',  // Exclude shadcn/ui components
  ],
  coverageThreshold: {
    global: {
      lines: 80,
      statements: 80,
    },
  },
  coverageReporters: [
    'text',              // Terminal summary
    'html',              // HTML report in coverage/ directory
    'lcov',              // LCOV for tooling integration
  ],
  modulePathIgnorePatterns: ['<rootDir>/.next/'],
}

// Export config with Next.js integration
module.exports = createJestConfig(customJestConfig)
