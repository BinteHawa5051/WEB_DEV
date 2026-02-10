import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Users, Search, Award, Briefcase } from 'lucide-react';
import { judgesAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const Judges: React.FC = () => {
  const { user } = useAuth();
  const [searchTerm, setSearchTerm] = useState('');
  const [specializationFilter, setSpecializationFilter] = useState('');

  const { data: judgesData, isLoading } = useQuery(
    ['judges', specializationFilter],
    () => judgesAPI.getJudges({
      court_id: user?.court_id,
      specialization: specializationFilter || undefined
    })
  );

  const judges = judgesData?.data || [];

  const filteredJudges = judges.filter((judge: any) =>
    judge.user?.full_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Judges</h1>
          <p className="text-gray-600">Manage judge profiles and workload</p>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search judges by name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
          <select
            value={specializationFilter}
            onChange={(e) => setSpecializationFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Specializations</option>
            <option value="civil">Civil</option>
            <option value="criminal">Criminal</option>
            <option value="family">Family</option>
            <option value="tax">Tax</option>
            <option value="constitutional">Constitutional</option>
          </select>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredJudges.map((judge: any) => (
              <div key={judge.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-center mb-4">
                  <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <Users className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {judge.user?.full_name || `Judge ${judge.id}`}
                    </h3>
                    <p className="text-sm text-gray-500">
                      {judge.experience_years} years experience
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-sm font-medium text-gray-500">Specializations</p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {judge.specializations?.map((spec: string, idx: number) => (
                        <span
                          key={idx}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800"
                        >
                          {spec}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-500">Workload</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {judge.current_workload || 0}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-500">Disposal Rate</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {judge.disposal_rate?.toFixed(1) || '0.0'}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between pt-3 border-t">
                    <div className="flex items-center">
                      <Award className="h-4 w-4 text-gray-400 mr-1" />
                      <span className="text-sm text-gray-600">
                        Score: {judge.performance_score?.toFixed(1) || '0.0'}
                      </span>
                    </div>
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                      judge.is_available
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {judge.is_available ? 'Available' : 'Unavailable'}
                    </span>
                  </div>

                  <button className="w-full mt-4 px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {filteredJudges.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No judges found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search or filter criteria
            </p>
          </div>
        )}
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center">
          <Briefcase className="h-8 w-8 text-blue-600 mr-3" />
          <div>
            <h3 className="text-lg font-medium text-blue-900">
              AI/ML Judge-Case Matching (Coming Soon)
            </h3>
            <p className="text-blue-700 mt-1">
              ML-based optimal judge assignment recommendations based on expertise, workload, and historical performance will be available here.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Judges;