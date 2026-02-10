import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { FileText, Upload, Search, Download, Shield } from 'lucide-react';
import { documentsAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const Documents: React.FC = () => {
  const { user } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');

  const { data: searchResults, isLoading } = useQuery(
    ['documents-search', searchQuery],
    () => documentsAPI.semanticSearch(searchQuery, undefined, undefined, 20),
    { enabled: searchQuery.length > 2 }
  );

  const results = searchResults?.data?.results || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600">Search and manage legal documents</p>
        </div>
        <button className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
          <Upload className="h-5 w-5 mr-2" />
          Upload Document
        </button>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Semantic Document Search
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search legal documents using natural language..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <p className="mt-2 text-sm text-gray-500">
            Try: "cases related to property disputes" or "judgments about contract law"
          </p>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : searchQuery.length > 2 ? (
          <div className="space-y-4">
            {results.map((doc: any) => (
              <div
                key={doc.document_id}
                className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <FileText className="h-5 w-5 text-gray-400 mr-2" />
                      <h3 className="font-medium text-gray-900">{doc.title}</h3>
                      <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                        {doc.document_type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mt-1">
                      Case: {doc.case_number}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">{doc.snippet}</p>
                    <div className="flex items-center mt-2 text-xs text-gray-500">
                      <span>Relevance: {(doc.relevance_score * 100).toFixed(0)}%</span>
                      <span className="mx-2">•</span>
                      <span>{new Date(doc.upload_date).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <button className="ml-4 p-2 text-gray-400 hover:text-gray-600">
                    <Download className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))}
            {results.length === 0 && (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No documents found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Try different search terms or keywords
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12">
            <Search className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">
              Start searching
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Enter at least 3 characters to search documents
            </p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center mb-4">
            <Shield className="h-6 w-6 text-green-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">
              Document Verification
            </h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            All documents are secured with digital signatures and cryptographic verification.
          </p>
          <div className="space-y-2 text-sm">
            <div className="flex items-center text-gray-600">
              <div className="h-2 w-2 bg-green-500 rounded-full mr-2"></div>
              SHA-256 hash verification
            </div>
            <div className="flex items-center text-gray-600">
              <div className="h-2 w-2 bg-green-500 rounded-full mr-2"></div>
              Digital signature validation
            </div>
            <div className="flex items-center text-gray-600">
              <div className="h-2 w-2 bg-green-500 rounded-full mr-2"></div>
              Tamper-proof document chain
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-6">
          <h3 className="text-lg font-medium text-indigo-900 mb-2">
            AI/ML Features (Coming Soon)
          </h3>
          <div className="space-y-2 text-sm text-indigo-700">
            <p>• Semantic search with TensorFlow.js</p>
            <p>• Named Entity Recognition (NER)</p>
            <p>• Citation network visualization</p>
            <p>• Legal entity extraction</p>
            <p>• Similar case recommendations</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Documents;