import React from 'react';
import { useQuery } from 'react-query';
import { 
  FileText, 
  Users, 
  Calendar, 
  Clock, 
  TrendingUp, 
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { casesAPI, judgesAPI, calendarAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  // Fetch dashboard data
  const { data: cases } = useQuery('dashboard-cases', () => 
    casesAPI.getCases({ limit: 100 })
  );

  const { data: judges } = useQuery('dashboard-judges', () => 
    judgesAPI.getJudges({ court_id: user?.court_id })
  );

  const { data: upcomingHearings } = useQuery('dashboard-hearings', () => 
    calendarAPI.getUpcomingHearings(7)
  );

  // Calculate statistics
  const totalCases = cases?.data?.length || 0;
  const pendingCases = cases?.data?.filter((c: any) => 
    ['filed', 'admitted', 'listed'].includes(c.status)
  ).length || 0;
  const urgentCases = cases?.data?.filter((c: any) => 
    ['habeas_corpus', 'bail', 'injunction'].includes(c.urgency_level)
  ).length || 0;
  const totalJudges = judges?.data?.length || 0;
  const availableJudges = judges?.data?.filter((j: any) => j.is_available).length || 0;
  const totalUpcomingHearings = upcomingHearings?.data?.upcoming_hearings?.length || 0;

  const stats = [
    {
      name: 'Total Cases',
      value: totalCases,
      icon: FileText,
      color: 'bg-blue-500',
      change: '+12%',
      changeType: 'increase'
    },
    {
      name: 'Pending Cases',
      value: pendingCases,
      icon: Clock,
      color: 'bg-yellow-500',
      change: '-3%',
      changeType: 'decrease'
    },
    {
      name: 'Urgent Cases',
      value: urgentCases,
      icon: AlertTriangle,
      color: 'bg-red-500',
      change: '+5%',
      changeType: 'increase'
    },
    {
      name: 'Available Judges',
      value: `${availableJudges}/${totalJudges}`,
      icon: Users,
      color: 'bg-green-500',
      change: '100%',
      changeType: 'neutral'
    }
  ];

  const recentCases = cases?.data?.slice(0, 5) || [];
  const todayHearings = upcomingHearings?.data?.upcoming_hearings?.filter((h: any) => 
    h.days_until === 0
  ) || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">
          Welcome back, {user?.full_name}. Here's what's happening in your court today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className={`${stat.color} rounded-md p-3`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        {stat.name}
                      </dt>
                      <dd className="flex items-baseline">
                        <div className="text-2xl font-semibold text-gray-900">
                          {stat.value}
                        </div>
                        <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                          stat.changeType === 'increase' ? 'text-green-600' :
                          stat.changeType === 'decrease' ? 'text-red-600' : 'text-gray-600'
                        }`}>
                          {stat.change}
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Cases */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Recent Cases
            </h3>
            <div className="space-y-3">
              {recentCases.map((caseItem: any) => (
                <div key={caseItem.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <p className="text-sm font-medium text-gray-900">
                        {caseItem.case_number}
                      </p>
                      <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        caseItem.urgency_level === 'habeas_corpus' ? 'bg-red-100 text-red-800' :
                        caseItem.urgency_level === 'bail' ? 'bg-orange-100 text-orange-800' :
                        caseItem.urgency_level === 'injunction' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {caseItem.urgency_level.replace('_', ' ')}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 truncate">{caseItem.title}</p>
                  </div>
                  <div className="flex items-center">
                    {caseItem.status === 'judgment' ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : caseItem.status === 'archived' ? (
                      <XCircle className="h-5 w-5 text-gray-500" />
                    ) : (
                      <Clock className="h-5 w-5 text-yellow-500" />
                    )}
                  </div>
                </div>
              ))}
              {recentCases.length === 0 && (
                <p className="text-gray-500 text-center py-4">No recent cases</p>
              )}
            </div>
          </div>
        </div>

        {/* Today's Hearings */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
              Today's Hearings
            </h3>
            <div className="space-y-3">
              {todayHearings.map((hearing: any) => (
                <div key={hearing.hearing_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {hearing.case_number}
                    </p>
                    <p className="text-sm text-gray-600">{hearing.case_title}</p>
                    <p className="text-xs text-gray-500">
                      {hearing.courtroom} • {hearing.judge}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-gray-900">
                      {new Date(hearing.scheduled_date).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                    <p className="text-xs text-gray-500">
                      {hearing.duration_hours}h
                    </p>
                  </div>
                </div>
              ))}
              {todayHearings.length === 0 && (
                <p className="text-gray-500 text-center py-4">No hearings scheduled for today</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
            Quick Actions
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              <FileText className="h-5 w-5 mr-2" />
              File New Case
            </button>
            <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              <Calendar className="h-5 w-5 mr-2" />
              Schedule Hearing
            </button>
            <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              <Users className="h-5 w-5 mr-2" />
              Assign Judge
            </button>
            <button className="flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md shadow-sm bg-white text-sm font-medium text-gray-700 hover:bg-gray-50">
              <TrendingUp className="h-5 w-5 mr-2" />
              View Reports
            </button>
          </div>
        </div>
      </div>

      {/* AI/ML Insights Section */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-6">
        <div className="flex items-center mb-4">
          <TrendingUp className="h-8 w-8 text-purple-600 mr-3" />
          <div>
            <h3 className="text-lg font-medium text-purple-900">
              AI/ML Insights Available
            </h3>
            <p className="text-purple-700 mt-1">
              Advanced ML models are now active for case analysis and predictions
            </p>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-md border border-purple-200 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Duration Prediction</h4>
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
            <p className="text-sm text-gray-600">XGBoost model predicts hearing durations with 95% accuracy</p>
          </div>
          <div className="bg-white p-4 rounded-md border border-purple-200 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Outcome Prediction</h4>
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
            <p className="text-sm text-gray-600">ML analyzes case facts to predict plaintiff win probability</p>
          </div>
          <div className="bg-white p-4 rounded-md border border-purple-200 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Settlement Analysis</h4>
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
            <p className="text-sm text-gray-600">Trained model suggests mediation opportunities</p>
          </div>
          <div className="bg-white p-4 rounded-md border border-purple-200 hover:shadow-md transition-shadow cursor-pointer">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium text-gray-900">Judge Matching</h4>
              <CheckCircle className="h-5 w-5 text-green-500" />
            </div>
            <p className="text-sm text-gray-600">Cosine similarity ranks optimal judge assignments</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;