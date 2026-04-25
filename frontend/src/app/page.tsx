"use client";

import { useState } from "react";
import { Upload, Link as LinkIcon, FileText, ChevronRight, Loader2, Download, CheckCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

interface ResultData {
  status: string;
  scores: {
    old_ats_score: number;
    new_ats_score: number;
  };
  missing_keywords_found: string[];
  resume_pdf: string;
  cover_letter_pdf: string;
}

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<ResultData | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !url) {
      setError("Please provide both a resume PDF and a Job Description URL.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("resume_file", file);
    formData.append("jd_url", url);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000"}/api/optimize-resume`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to optimize resume");
      }

      const data = await response.json();
      setResult(data);
    } catch (err: unknown) {
        if (err instanceof Error) {
            setError(err.message || "An unexpected error occurred.");
        } else {
            setError("An unexpected error occurred.");
        }
    } finally {
      setLoading(false);
    }
  };

  const downloadPDF = (base64String: string, filename: string) => {
    const linkSource = `data:application/pdf;base64,${base64String}`;
    const downloadLink = document.createElement("a");
    downloadLink.href = linkSource;
    downloadLink.download = filename;
    downloadLink.click();
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <header className="bg-white border-b border-gray-200 py-6 px-8 sticky top-0 z-10 shadow-sm">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <FileText className="text-white h-6 w-6" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 tracking-tight">ATS-Crusher</h1>
          </div>
          <p className="text-gray-500 font-medium text-sm hidden sm:block">AI-Powered Resume Optimization</p>
        </div>
      </header>

      <main className="flex-grow py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
        <div className="max-w-3xl w-full space-y-8">

          {/* Input Section */}
          <div className="bg-white shadow-xl shadow-gray-200/50 rounded-2xl overflow-hidden border border-gray-100">
            <div className="p-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">Optimize Your Resume for the ATS</h2>
              <form onSubmit={handleSubmit} className="space-y-6">

                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Upload Current Resume (PDF)</label>
                  <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-xl hover:border-blue-500 hover:bg-blue-50 transition-colors group cursor-pointer relative">
                    <div className="space-y-2 text-center">
                      <Upload className="mx-auto h-10 w-10 text-gray-400 group-hover:text-blue-500 transition-colors" />
                      <div className="flex text-sm text-gray-600 justify-center">
                        <label htmlFor="file-upload" className="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-blue-500">
                          <span>Upload a file</span>
                          <input id="file-upload" name="file-upload" type="file" accept=".pdf" className="sr-only" onChange={handleFileChange} />
                        </label>
                        <p className="pl-1">or drag and drop</p>
                      </div>
                      <p className="text-xs text-gray-500">{file ? file.name : "PDF up to 10MB"}</p>
                    </div>
                  </div>
                </div>

                {/* URL Input */}
                <div>
                  <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">Target Job Description URL</label>
                  <div className="relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <LinkIcon className="h-5 w-5 text-gray-400" />
                    </div>
                    <input
                      type="url"
                      name="url"
                      id="url"
                      className="focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 sm:text-sm border-gray-300 rounded-xl py-3 border outline-none"
                      placeholder="https://company.com/careers/job-123"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                    />
                  </div>
                </div>

                {error && (
                  <div className="p-4 bg-red-50 text-red-700 text-sm rounded-xl border border-red-100 flex items-center">
                    <span className="font-medium mr-2">Error:</span> {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-70 disabled:cursor-not-allowed transition-all"
                >
                  {loading ? (
                    <span className="flex items-center">
                      <Loader2 className="animate-spin -ml-1 mr-2 h-5 w-5" />
                      Analyzing & Optimizing...
                    </span>
                  ) : (
                    <span className="flex items-center">
                      Crush the ATS <ChevronRight className="ml-2 h-5 w-5" />
                    </span>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Results Section */}
          <AnimatePresence>
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white shadow-xl shadow-gray-200/50 rounded-2xl overflow-hidden border border-gray-100"
              >
                <div className="p-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Optimization Complete!</h3>

                  {/* Scores */}
                  <div className="grid grid-cols-2 gap-8 mb-10">
                    <div className="bg-gray-50 rounded-2xl p-6 border border-gray-100 text-center relative overflow-hidden">
                      <div className="absolute top-0 left-0 w-full h-1 bg-gray-200"></div>
                      <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">Original ATS Score</p>
                      <p className="text-5xl font-black text-gray-400">{result.scores.old_ats_score}<span className="text-2xl text-gray-300">/100</span></p>
                    </div>
                    <div className="bg-green-50 rounded-2xl p-6 border border-green-100 text-center relative overflow-hidden shadow-sm">
                      <div className="absolute top-0 left-0 w-full h-1 bg-green-500"></div>
                      <p className="text-sm font-medium text-green-700 uppercase tracking-wider mb-2">New ATS Score</p>
                      <p className="text-5xl font-black text-green-600">{result.scores.new_ats_score}<span className="text-2xl text-green-300">/100</span></p>
                    </div>
                  </div>

                  {/* Keywords Added */}
                  <div className="mb-10">
                    <h4 className="text-sm font-bold text-gray-900 uppercase tracking-wider mb-4 flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-blue-500" />
                      Keywords Successfully Integrated
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {result.missing_keywords_found.map((kw: string, i: number) => (
                        <span key={i} className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800 border border-blue-200">
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Downloads */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <button
                      onClick={() => downloadPDF(result.resume_pdf, "Optimized_Resume.pdf")}
                      className="flex items-center justify-center py-4 px-4 border border-transparent rounded-xl shadow-sm text-sm font-bold text-white bg-gray-900 hover:bg-gray-800 transition-colors"
                    >
                      <Download className="mr-2 h-5 w-5" /> Download ATS Resume
                    </button>
                    <button
                      onClick={() => downloadPDF(result.cover_letter_pdf, "Cover_Letter.pdf")}
                      className="flex items-center justify-center py-4 px-4 border border-gray-300 rounded-xl shadow-sm text-sm font-bold text-gray-700 bg-white hover:bg-gray-50 transition-colors"
                    >
                      <Download className="mr-2 h-5 w-5" /> Download Cover Letter
                    </button>
                  </div>

                </div>
              </motion.div>
            )}
          </AnimatePresence>

        </div>
      </main>
    </div>
  );
}
