import { ProjectAnalyzer } from '../src/utils/projectAnalyzer';
import { AIAnalyzer } from '../src/utils/aiAnalyzer';
import { ProjectAnalysis, ProjectAnalyzerOptions } from '../src/types';
import path from 'path';
import fs from 'fs-extra';

describe('Project Analysis', () => {
  const projectPath = path.resolve(__dirname, '..');
  const testProjectPath = path.resolve(__dirname, 'test-project');

  beforeAll(async () => {
    // Create test project directory with mock package.json
    await fs.ensureDir(testProjectPath);
    await fs.writeJson(path.join(testProjectPath, 'package.json'), {
      dependencies: {
        'vite': '^4.0.0',
        '@vitejs/plugin-react': '^3.0.0'
      }
    });
  });

  afterAll(async () => {
    // Clean up test project
    await fs.remove(testProjectPath);
  });

  describe('ProjectAnalyzer', () => {
    let analyzer: ProjectAnalyzer;

    beforeEach(() => {
      analyzer = new ProjectAnalyzer(testProjectPath);
    });

    test('should perform basic analysis', async () => {
      const analysis = await analyzer.analyzeProject();
      
      // Basic analysis checks
      expect(analysis).toBeDefined();
      expect(analysis.framework).toBeDefined();
      expect(analysis.dependencies).toBeDefined();
      expect(analysis.tsConfig).toBeDefined();
      expect(analysis.routingStructure).toBeDefined();
    });

    test('should handle custom config files', async () => {
      const options: ProjectAnalyzerOptions = {
        config: ['custom.config.js']
      };
      const analysis = await analyzer.analyzeProject(options);
      
      expect(analysis.framework).toBe('vite');
    });
  });

  describe('AIAnalyzer', () => {
    let analyzer: AIAnalyzer;

    beforeEach(() => {
      analyzer = new AIAnalyzer(projectPath);
    });

    test('should analyze codebase structure', async () => {
      // Skip if no API key
      if (!process.env.ANTHROPIC_API_KEY) {
        console.log('Skipping AI analysis test - no API key found');
        return;
      }

      const analysis = await analyzer.analyzeCodebase();
      
      // AI analysis checks
      expect(analysis).toBeDefined();
      expect(analysis.routing).toBeDefined();
      expect(analysis.routing.type).toBeDefined();
      expect(analysis.routing.suggestedNextjsStructure).toBeDefined();
      expect(analysis.dependencies).toBeDefined();
      expect(analysis.configuration).toBeDefined();
    });

    test('should handle missing API key gracefully', async () => {
      // Temporarily remove API key
      const originalApiKey = process.env.ANTHROPIC_API_KEY;
      delete process.env.ANTHROPIC_API_KEY;

      try {
        await expect(analyzer.analyzeCodebase()).rejects.toThrow('Could not resolve authentication method');
      } finally {
        // Restore API key
        process.env.ANTHROPIC_API_KEY = originalApiKey;
      }
    });

    test('should handle missing files gracefully', async () => {
      const invalidAnalyzer = new AIAnalyzer('/non/existent/path');
      await expect(invalidAnalyzer.analyzeCodebase()).rejects.toThrow('ENOENT');
    });
  });
}); 