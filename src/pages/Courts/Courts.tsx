import React, { useState, useEffect } from 'react';
import { Building2, MapPin, Scale, Users, TrendingUp, AlertCircle } from 'lucide-react';
import { courtsAPI } from '../../services/api';
import toast from 'react-hot-toast';

interface Court {
  id: number;
  name: string;
  level: string;
  jurisdiction: string;
  location: string;
  parent_court_id: number | null;
  parent_court_name: string | null;
  is_active: boolean;
}

interface CourtStats {
  court_id: number;
  court_name: string;
  level: string;
  cases_count: number;
  judges_count: number;
  utilization: number;
}

interface HierarchyNode {
  id: number;
  name: string;
  level: string;
  jurisdiction: string;
  location: string;
  children: HierarchyNode[];
}

const Courts: React.FC = () => {
  const [courts, setCourts] = useState<Court[]>([]);
  const [hierarchy, setHierarchy] = useState<HierarchyNode[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'list' | 'hierarchy' | 'stats'>('list');
  const [levelFilter, setLevelFilter] = useState<string>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [courtsData, hierarchyData, statsData] = await Promise.all([
        courtsAPI.getCourts(),
        courtsAPI.getHierarchy(),
        courtsAPI.getStatistics()
      ]);
      
      setCourts(courtsData);
      setHierarchy(hierarchyData.hierarchy);
      setStatistics(statsData);
    } catch (error: any) {
      toast.error('Failed to load courts data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getLevelBadgeColor = (level: string) => {
    switch (level) {
      case 'supreme_court': return 'bg-purple-100 text-purple-800';
      case 'high_court': return 'bg-blue-100 text-blue-800';
      case 'district_court': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getUtilizationColor = (utilization: number) => {
    if (utilization < 50) return 'text-green-600';
    if (utilization < 80) return 'text-yellow-600';
    return 'text-red-600';
  };

  const renderHierarchyNode = (node: HierarchyNode, depth: number = 0) => (
    <div key={node.id} style={{ marginLeft: `${depth * 2}rem` }} className="mb-4">
      <div className="bg-white rounded-lg shadow p-4 border-l-4 border-indigo-500">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-lg">{node.name}</h3>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
              <span className={`px-2 py-1 rounded ${getLevelBadgeColor(node.level)}`}>
                {node.level.replace('_', ' ').toUpperCase()}
              </span>
              <span className="flex items-center gap-1">
                <Scale className="w-4 h-4" />
                {node.jurisdiction}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" />
                {node.location}
              </span>
            </div>
          </div>
        </div>
      </div>
      {node.children && node.children.length > 0 && (
        <div className="mt-2">
          {node.children.map(child => renderHierarchyNode(child, depth + 1))}
        </div>
      )}
    </div>
  );

  const filteredCourts = levelFilter === 'all' 
    ? courts 
    : courts.filter(c => c.level === levelFilter);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Court System Management</h1>
        <p className="text-gray-600 mt-2">Multi-level court hierarchy and statistics</p>
      </div>

      {/* Summary Cards */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Courts</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_courts}</p>
              </div>
              <Building2 className="w-12 h-12 text-indigo-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Cases</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_cases}</p>
              </div>
              <Scale className="w-12 h-12 text-blue-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Judges</p>
                <p className="text-2xl font-bold text-gray-900">{statistics.total_judges}</p>
              </div>
              <Users className="w-12 h-12 text-green-600" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Avg Utilization</p>
                <p className="text-2xl font-bold text-gray-900">
                  {statistics.court_statistics.length > 0
                    ? Math.round(
                        statistics.court_statistics.reduce((sum: number, c: CourtStats) => sum + c.utilization, 0) /
                        statistics.court_statistics.length
                      )
                    : 0}%
                </p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-600" />
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow mb-6">
        <div className="border-b border-gray-200">
          <nav className="flex -mb-px">
            <button
              onClick={() => setActiveTab('list')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'list'
                  ? 'border-b-2 border-indigo-500 text-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Courts List
            </button>
            <button
              onClick={() => setActiveTab('hierarchy')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'hierarchy'
                  ? 'border-b-2 border-indigo-500 text-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Hierarchy View
            </button>
            <button
              onClick={() => setActiveTab('stats')}
              className={`px-6 py-3 text-sm font-medium ${
                activeTab === 'stats'
                  ? 'border-b-2 border-indigo-500 text-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Statistics
            </button>
          </nav>
        </div>

        <div className="p-6">
          {/* Courts List Tab */}
          {activeTab === 'list' && (
            <div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filter by Level
                </label>
                <select
                  value={levelFilter}
                  onChange={(e) => setLevelFilter(e.target.value)}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="all">All Levels</option>
                  <option value="supreme_court">Supreme Court</option>
                  <option value="high_court">High Court</option>
                  <option value="district_court">District Court</option>
                </select>
              </div>

              <div className="space-y-4">
                {filteredCourts.map((court) => (
                  <div key={court.id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-semibold text-gray-900">{court.name}</h3>
                          <span className={`px-2 py-1 rounded text-xs ${getLevelBadgeColor(court.level)}`}>
                            {court.level.replace('_', ' ').toUpperCase()}
                          </span>
                          {!court.is_active && (
                            <span className="px-2 py-1 rounded text-xs bg-red-100 text-red-800">
                              Inactive
                            </span>
                          )}
                        </div>
                        
                        <div className="mt-2 grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-2">
                            <Scale className="w-4 h-4" />
                            <span>Jurisdiction: {court.jurisdiction}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <MapPin className="w-4 h-4" />
                            <span>Location: {court.location}</span>
                          </div>
                          {court.parent_court_name && (
                            <div className="flex items-center gap-2">
                              <Building2 className="w-4 h-4" />
                              <span>Parent: {court.parent_court_name}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Hierarchy Tab */}
          {activeTab === 'hierarchy' && (
            <div>
              <div className="mb-4 bg-blue-50 border border-blue-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                  <div>
                    <p className="text-sm text-blue-900 font-medium">Court Hierarchy Structure</p>
                    <p className="text-sm text-blue-700 mt-1">
                      Visualizes the multi-level court system from Supreme Court down to District Courts
                    </p>
                  </div>
                </div>
              </div>
              
              {hierarchy.length > 0 ? (
                <div className="space-y-4">
                  {hierarchy.map(node => renderHierarchyNode(node))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-8">No hierarchy data available</p>
              )}
            </div>
          )}

          {/* Statistics Tab */}
          {activeTab === 'stats' && statistics && (
            <div>
              <div className="space-y-4">
                {statistics.court_statistics.map((stat: CourtStats) => (
                  <div key={stat.court_id} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-semibold text-gray-900">{stat.court_name}</h3>
                        <span className={`text-xs px-2 py-1 rounded ${getLevelBadgeColor(stat.level)}`}>
                          {stat.level.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                      <div className={`text-2xl font-bold ${getUtilizationColor(stat.utilization)}`}>
                        {stat.utilization}%
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-gray-600">Cases</p>
                        <p className="text-lg font-semibold text-gray-900">{stat.cases_count}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Judges</p>
                        <p className="text-lg font-semibold text-gray-900">{stat.judges_count}</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Cases per Judge</p>
                        <p className="text-lg font-semibold text-gray-900">
                          {stat.judges_count > 0 ? Math.round(stat.cases_count / stat.judges_count) : 0}
                        </p>
                      </div>
                    </div>
                    
                    <div className="mt-3">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            stat.utilization < 50 ? 'bg-green-500' :
                            stat.utilization < 80 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${Math.min(stat.utilization, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Courts;
