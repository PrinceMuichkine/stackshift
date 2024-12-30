const { execSync } = require('child_process');

describe('CLI Commands', () => {
    test('analyze command should execute successfully', () => {
        const output = execSync('node dist/cli.js analyze . --no-interactive').toString();
        expect(output).toContain('Analyzing project structure...');
    });

    test('analyze command should handle custom config files', () => {
        const output = execSync('node dist/cli.js analyze . -c custom.config.js --no-interactive').toString();
        expect(output).toContain('Analyzing project structure...');
    });

    test('analyze command should handle missing project path', () => {
        const output = execSync('node dist/cli.js analyze --no-interactive').toString();
        expect(output).toContain('Analyzing project structure...');
    });

    test('invalid command should display help information', () => {
        try {
            execSync('node dist/cli.js invalid');
        } catch (error) {
            expect(error.message).toContain('Invalid command');
        }
    });

    test('analyze command should handle no AI key gracefully', () => {
        const output = execSync('node dist/cli.js analyze . --no-ai --no-interactive').toString();
        expect(output).toContain('Warning: No Anthropic API key found');
        expect(output).toContain('Analyzing project structure...');
    });
}); 