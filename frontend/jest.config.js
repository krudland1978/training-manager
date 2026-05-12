export default {
  testEnvironment: 'jsdom',
  setupFilesAfterFramework: ['@testing-library/jest-dom'],
  transform: {
    '^.+\\.[jt]sx?$': ['babel-jest', { presets: ['@babel/preset-env', ['@babel/preset-react', { runtime: 'automatic' }]] }],
  },
  moduleNameMapper: {
    '\\.(css|svg)$': '<rootDir>/tests/__mocks__/fileMock.js',
    '^(\\.{1,2}/.*)\\.jsx?$': '$1',
  },
  extensionsToTreatAsEsm: [],
  testMatch: ['<rootDir>/tests/**/*.test.{js,jsx}'],
}
