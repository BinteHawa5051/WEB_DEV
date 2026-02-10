import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Clock, AlertCircle, CheckCircle, Calendar } from 'lucide-react';
import { schedulingAPI, casesAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const Scheduling: React.FC = () => {
  const { user } = useAuth();
  const [selectedCase, setSelectedCase] = useState<number | null>(null);

  const { data: casesData } = useQuery(
    'pending-cases',
    () => casesAPI.getCases({ status: 'admitted', court_id: user?.court_id })
  );

  const { data: slotsData, isLoading: slotsLoading } = useQuery(
    ['available-slots', selectedCase],
    () => schedulingAPI.findSlots({
      case_id: selectedCase,
      constraints: {
        judge_expertise_required: ['civil'],
        min_advance_days: 7,
        max_daily_hours: 6.0
      },
      priority_weight: 1.0
    }),
    { enabled: !!selectedCase }
  );

  const { data: optimizationReport } = useQuery(
    'optimization-report',
    () => schedulingAPI.getOptimizationReport(user?.court_id)
  );

  const cases = casesData?.data || [];
  const slots = slotsData?.data?.suggested_slots || [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Intelligent Scheduling</h1>
        <p className="text-gray-600">AI-powered case scheduling and optimization</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Select Case to Schedule
            </h2>
            <div className="space-y-2">
              {cases.map((caseItem: any) => (
                <div
                  key={caseItem.id}
                  onClick={() => setSelectedCase(caseItem.id)}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedCase === caseItem.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{caseItem.case_number}</p>
                      <p className="text-sm text-gray-600">{caseItem.title}</p>
                    </div>
                    <span className="text-xs text-gray-500">
                      {caseItem.urgency_level.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              ))}
              {cases.length === 0 && (
                <p className="text-gray-500 text-center py-4">
                  No cases available for scheduling
                </p>
              )}
            </div>
          </div>

          {selectedCase && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Available Time Slots
              </h2>
              {slotsLoading ? (
                <div className="flex justify-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                </div>
              ) : (
                <div className="space-y-3">
                  {slots.map((slot: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center">
                            <Calendar className="h-5 w-5 text-gray-400 mr-2" />
                            <p className="font-medium text-gray-900">
                              {new Date(slot.datetime).toLocaleDateString()} at{' '}
                              {new Date(slot.datetime).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </p>
                          </div>
                          <p className="text-sm text-gray-600 mt-1">
                            {slot.judge_name} • {slot.courtroom_name}
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            Duration: {slot.estimated_duration}h
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="flex items-center text-sm text-green-600">
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Priority: {slot.priority_score.toFixed(1)}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {slots.length === 0 && (
                    <p className="text-gray-500 text-center py-4">
                      No available slots found
                    </p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">
              Scheduling Metrics
            </h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Total Cases</p>
                <p className="text-2xl font-bold text-gray-900">
                  {optimizationReport?.data?.total_cases || 0}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Pending Cases</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {optimizationReport?.data?.pending_cases || 0}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Average Delay</p>
                <p className="text-2xl font-bold text-red-600">
                  {optimizationReport?.data?.average_delay_days?.toFixed(0) || 0} days
                </p>
              </div>
            </div>
          </div>

          <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
            <div className="flex items-start">
              <Clock className="h-6 w-6 text-purple-600 mr-3 mt-1" />
              <div>
                <h3 className="text-sm font-medium text-purple-900 mb-2">
                  AI/ML Optimization (Coming Soon)
                </h3>
                <p className="text-sm text-purple-700">
                  Advanced ML algorithms will optimize scheduling based on:
                </p>
                <ul className="mt-2 text-xs text-purple-600 space-y-1">
                  <li>• Case duration predictions</li>
                  <li>• Judge workload balancing</li>
                  <li>• Lawyer availability patterns</li>
                  <li>• Historical scheduling data</li>
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-sm font-semibold text-gray-900 mb-3">
              Scheduling Constraints
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center text-gray-600">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                Min 7 days advance notice
              </div>
              <div className="flex items-center text-gray-600">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                Max 6 hours daily court time
              </div>
              <div className="flex items-center text-gray-600">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                Judge expertise matching
              </div>
              <div className="flex items-center text-gray-600">
                <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                Conflict prevention
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Scheduling;