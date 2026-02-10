import React, { useState } from 'react';
import { Search, Clock, AlertTriangle, Calendar, TrendingUp, FileText, Info } from 'lucide-react';
import { casesAPI } from '../../services/api';
import toast from 'react-hot-toast';

interface CaseDelay {
  case_number: string;
  case_title: string;
  filed_date: string;
  expected_days: number;
  actual_days: number;
  delay_days: number;
  severity: string;
  status: string;
  next_hearing_date: string | null;
  adjournment_count: number;
  reasons: string[];
}

const DelayJustification: React.FC = () => {
  const [caseNumber, setCaseNumber] = useState('');
  const [caseDelay, setCaseDelay] = useState<CaseDelay | null>(null);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!caseNumber.trim()) {
      toast.error('Please enter a case number');
      return;
    }

    try {
      setLoading(true);
      setSearched(true);
      
      // Extract case ID from case number (assuming format like CASE-123)
      const caseId = parseInt(caseNumber.split('-')[1] || caseNumber);
      
      if (isNaN(caseId)) {
        toast.error('Invalid case number format');
        return;
      }

      const response = await casesAPI.getCaseDelays(caseId);
      setCaseDelay(response);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Case not found');
      setCaseDelay(null);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'moderate': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-green-100 text-green-800 border-green-300';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <Clock className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 p-6">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <FileText className="w-12 h-12 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Case Delay Transparency Portal
          </h1>
          <p className="text-gray-600 text-lg">
            Track your case status and understand any delays
          </p>
        </div>

        {/* Info Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-blue-900">
              <p className="font-medium mb-1">Public Transparency Initiative</p>
              <p>
                This portal provides real-time information about case delays, scheduling history, 
                and projected hearing dates. Enter your case number to view detailed information.
              </p>
            </div>
          </div>
        </div>

        {/* Search Box */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Enter Case Number
          </label>
          <div className="flex gap-3">
            <input
              type="text"
              value={caseNumber}
              onChange={(e) => setCaseNumber(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="e.g., CASE-123 or 123"
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <button
              onClick={handleSearch}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 flex items-center gap-2 transition-colors"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Searching...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  Search
                </>
              )}
            </button>
          </div>
        </div>

        {/* Results */}
        {searched && !loading && (
          <>
            {caseDelay ? (
              <div className="space-y-6">
                {/* Case Overview */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Case Information</h2>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-600">Case Number</p>
                      <p className="text-lg font-semibold text-gray-900">{caseDelay.case_number}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Status</p>
                      <p className="text-lg font-semibold text-gray-900 capitalize">{caseDelay.status}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Filed Date</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {new Date(caseDelay.filed_date).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Next Hearing</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {caseDelay.next_hearing_date 
                          ? new Date(caseDelay.next_hearing_date).toLocaleDateString()
                          : 'Not scheduled'}
                      </p>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <p className="text-sm text-gray-600 mb-1">Case Title</p>
                    <p className="text-gray-900">{caseDelay.case_title}</p>
                  </div>
                </div>

                {/* Delay Analysis */}
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Delay Analysis</h2>
                  
                  <div className={`border-2 rounded-lg p-4 mb-4 ${getSeverityColor(caseDelay.severity)}`}>
                    <div className="flex items-center gap-3 mb-2">
                      {getSeverityIcon(caseDelay.severity)}
                      <span className="font-semibold text-lg capitalize">
                        {caseDelay.severity} Delay
                      </span>
                    </div>
                    <p className="text-sm">
                      This case has been delayed by <strong>{caseDelay.delay_days} days</strong> beyond 
                      the expected timeline.
                    </p>
                  </div>

                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-gray-600 mb-1">Expected Days</p>
                      <p className="text-2xl font-bold text-gray-900">{caseDelay.expected_days}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-gray-600 mb-1">Actual Days</p>
                      <p className="text-2xl font-bold text-gray-900">{caseDelay.actual_days}</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <p className="text-sm text-gray-600 mb-1">Adjournments</p>
                      <p className="text-2xl font-bold text-gray-900">{caseDelay.adjournment_count}</p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-2">
                      <span>Progress</span>
                      <span>{Math.round((caseDelay.actual_days / caseDelay.expected_days) * 100)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className={`h-3 rounded-full ${
                          caseDelay.delay_days > 30 ? 'bg-red-500' :
                          caseDelay.delay_days > 14 ? 'bg-orange-500' :
                          caseDelay.delay_days > 7 ? 'bg-yellow-500' : 'bg-green-500'
                        }`}
                        style={{ width: `${Math.min((caseDelay.actual_days / caseDelay.expected_days) * 100, 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Delay Reasons */}
                  {caseDelay.reasons && caseDelay.reasons.length > 0 && (
                    <div>
                      <h3 className="font-semibold text-gray-900 mb-2">Reasons for Delay</h3>
                      <ul className="space-y-2">
                        {caseDelay.reasons.map((reason, index) => (
                          <li key={index} className="flex items-start gap-2 text-gray-700">
                            <span className="text-blue-600 mt-1">•</span>
                            <span>{reason}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* What's Next */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg shadow-lg p-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">What's Next?</h2>
                  
                  <div className="space-y-3">
                    {caseDelay.next_hearing_date ? (
                      <div className="flex items-start gap-3">
                        <Calendar className="w-5 h-5 text-blue-600 mt-1" />
                        <div>
                          <p className="font-medium text-gray-900">Next Hearing Scheduled</p>
                          <p className="text-gray-700">
                            Your next hearing is on {new Date(caseDelay.next_hearing_date).toLocaleDateString('en-US', {
                              weekday: 'long',
                              year: 'numeric',
                              month: 'long',
                              day: 'numeric'
                            })}
                          </p>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start gap-3">
                        <Clock className="w-5 h-5 text-orange-600 mt-1" />
                        <div>
                          <p className="font-medium text-gray-900">Hearing Not Yet Scheduled</p>
                          <p className="text-gray-700">
                            The court is working to schedule your next hearing. You will be notified once a date is set.
                          </p>
                        </div>
                      </div>
                    )}
                    
                    <div className="flex items-start gap-3">
                      <TrendingUp className="w-5 h-5 text-green-600 mt-1" />
                      <div>
                        <p className="font-medium text-gray-900">Stay Updated</p>
                        <p className="text-gray-700">
                          Check this portal regularly for updates on your case status and hearing dates.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-lg p-12 text-center">
                <AlertTriangle className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">Case Not Found</h3>
                <p className="text-gray-600">
                  No case found with the number "{caseNumber}". Please check the case number and try again.
                </p>
              </div>
            )}
          </>
        )}

        {/* Help Section */}
        {!searched && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">How to Use This Portal</h2>
            <div className="space-y-3 text-gray-700">
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">1</span>
                <p>Enter your case number in the search box above</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">2</span>
                <p>View detailed information about your case status and any delays</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">3</span>
                <p>Check the projected next hearing date and reasons for any delays</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-semibold">4</span>
                <p>Return to this portal anytime for updated information</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DelayJustification;
