import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { ArrowLeft, FileText, Calendar, User, Clock } from 'lucide-react';
import { casesAPI } from '../../services/api';

const CaseDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: caseData, isLoading } = useQuery(
    ['case', id],
    () => casesAPI.getCase(Number(id)),
    { enabled: !!id }
  );

  const { data: historyData } = useQuery(
    ['case-history', id],
    () => casesAPI.getCaseHistory(Number(id)),
    { enabled: !!id }
  );

  const caseItem = caseData?.data;
  const history = historyData?.data || [];

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!caseItem) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Case not found</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center">
        <button
          onClick={() => navigate('/cases')}
          className="mr-4 p-2 hover:bg-gray-100 rounded-md"
        >
          <ArrowLeft className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{caseItem.case_number}</h1>
          <p className="text-gray-600">{caseItem.title}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Case Information</h2>
            <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <dt className="text-sm font-medium text-gray-500">Case Number</dt>
                <dd className="mt-1 text-sm text-gray-900">{caseItem.case_number}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Status</dt>
                <dd className="mt-1">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {caseItem.status}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Jurisdiction</dt>
                <dd className="mt-1 text-sm text-gray-900 capitalize">{caseItem.jurisdiction}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Case Type</dt>
                <dd className="mt-1 text-sm text-gray-900">{caseItem.case_type}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Urgency Level</dt>
                <dd className="mt-1">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                    {caseItem.urgency_level.replace('_', ' ')}
                  </span>
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Filing Date</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(caseItem.filing_date).toLocaleDateString()}
                </dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Complexity Score</dt>
                <dd className="mt-1 text-sm text-gray-900">{caseItem.complexity_score}/10</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-500">Public Interest Score</dt>
                <dd className="mt-1 text-sm text-gray-900">{caseItem.public_interest_score}/10</dd>
              </div>
              <div className="sm:col-span-2">
                <dt className="text-sm font-medium text-gray-500">Description</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {caseItem.description || 'No description provided'}
                </dd>
              </div>
            </dl>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Case History</h2>
            <div className="flow-root">
              <ul className="-mb-8">
                {history.map((event: any, idx: number) => (
                  <li key={event.id}>
                    <div className="relative pb-8">
                      {idx !== history.length - 1 && (
                        <span
                          className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                          aria-hidden="true"
                        />
                      )}
                      <div className="relative flex space-x-3">
                        <div>
                          <span className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center ring-8 ring-white">
                            <Clock className="h-5 w-5 text-white" />
                          </span>
                        </div>
                        <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                          <div>
                            <p className="text-sm text-gray-500">
                              Status changed from{' '}
                              <span className="font-medium text-gray-900">
                                {event.old_status || 'N/A'}
                              </span>{' '}
                              to{' '}
                              <span className="font-medium text-gray-900">
                                {event.new_status}
                              </span>
                            </p>
                            {event.notes && (
                              <p className="mt-1 text-sm text-gray-500">{event.notes}</p>
                            )}
                          </div>
                          <div className="whitespace-nowrap text-right text-sm text-gray-500">
                            {new Date(event.change_date).toLocaleDateString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
              {history.length === 0 && (
                <p className="text-gray-500 text-center py-4">No history available</p>
              )}
            </div>
          </div>

          {/* Connected Cases Section */}
          {caseItem.connected_cases && caseItem.connected_cases.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Connected Cases</h2>
              <div className="space-y-2">
                {caseItem.connected_cases.map((connectedId: number) => (
                  <div key={connectedId} className="flex items-center justify-between p-3 bg-gray-50 rounded-md hover:bg-gray-100 cursor-pointer" onClick={() => navigate(`/cases/${connectedId}`)}>
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-sm font-medium text-gray-900">Case #{connectedId}</span>
                    </div>
                    <ArrowLeft className="h-4 w-4 text-gray-400 transform rotate-180" />
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
            <div className="space-y-2">
              <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <Calendar className="h-5 w-5 mr-2" />
                Schedule Hearing
              </button>
              <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <FileText className="h-5 w-5 mr-2" />
                Upload Document
              </button>
              <button className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50">
                <User className="h-5 w-5 mr-2" />
                Assign Judge
              </button>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-sm font-medium text-blue-900 mb-2">
              AI/ML Insights (Coming Soon)
            </h3>
            <p className="text-sm text-blue-700">
              Predicted case duration, settlement probability, and optimal judge recommendations will appear here.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaseDetail;