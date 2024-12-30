import { useState } from 'react';
import type { NextPage } from 'next';
import { ProjectAnalyzer } from '../utils/projectAnalyzer';
import { MigrationPlanner } from '../utils/migrationPlanner';
import { ProjectAnalysis } from '../types';

const Home: NextPage = () => {
    const [projectPath, setProjectPath] = useState('');
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResults, setAnalysisResults] = useState<ProjectAnalysis | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsAnalyzing(true);

        try {
            const analyzer = new ProjectAnalyzer(projectPath);
            const results = await analyzer.analyzeProject();
            setAnalysisResults(results);
        } catch (error) {
            console.error('Analysis failed:', error);
        }

        setIsAnalyzing(false);
    };

    return (
        <main className="min-h-screen p-8">
            <h1 className="text-4xl font-bold mb-8">StackShift</h1>
            <div className="max-w-4xl">
                <h2 className="text-2xl font-semibold mb-4">Tech Stack Migration Assistant</h2>
                <div className="space-y-4">
                    <div className="p-6 bg-white rounded-lg shadow-md">
                        <h3 className="text-xl font-semibold mb-4">Analyze Your Project</h3>
                        <form onSubmit={handleSubmit}>
                            <div className="mb-4">
                                <label htmlFor="projectPath" className="block mb-2 font-bold">Project Path:</label>
                                <input
                                    type="text"
                                    id="projectPath"
                                    value={projectPath}
                                    onChange={(e) => setProjectPath(e.target.value)}
                                    className="w-full px-3 py-2 border rounded-md"
                                    required
                                />
                            </div>
                            <button
                                type="submit"
                                className="px-4 py-2 font-bold text-white bg-blue-500 rounded-md hover:bg-blue-600"
                                disabled={isAnalyzing}
                            >
                                {isAnalyzing ? 'Analyzing...' : 'Analyze'}
                            </button>
                        </form>
                    </div>
                    {analysisResults && (
                        <div className="p-6 bg-white rounded-lg shadow-md">
                            <h3 className="text-xl font-semibold mb-4">Analysis Results</h3>
                            <pre>{JSON.stringify(analysisResults, null, 2)}</pre>
                        </div>
                    )}
                </div>
            </div>
        </main>
    );
};

export default Home; 