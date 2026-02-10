import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight, AlertCircle, CheckCircle, Clock } from 'lucide-react';
import { calendarAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const Calendar: React.FC = () => {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'month' | 'week' | 'day'>('week');
  const [filters, setFilters] = useState({
    caseType: '',
    judge: '',
    urgency: '',
  });

  // Get capacity color based on workload percentage
  const getCapacityColor = (capacity: number) => {
    if (capacity < 50) return { bg: 'bg-green-100', text: 'text-green-800', label: 'Light', icon: CheckCircle };
    if (capacity < 80) return { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'Moderate', icon: Clock };
    return { bg: 'bg-red-100', text: 'text-red-800', label: 'Overloaded', icon: AlertCircle };
  };

  // Get week start date
  const getWeekStart = (date: Date) => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  };

  const weekStart = getWeekStart(currentDate);
  const weekStartStr = weekStart.toISOString().split('T')[0];

  const { data: weekData, isLoading } = useQuery(
    ['calendar-week', weekStartStr],
    () => calendarAPI.getWeekView(weekStartStr, user?.court_id),
    { enabled: view === 'week' }
  );

  const { data: upcomingHearings } = useQuery(
    'upcoming-hearings',
    () => calendarAPI.getUpcomingHearings(7)
  );

  const navigateWeek = (direction: 'prev' | 'next') => {
    const newDate = new Date(currentDate);
    newDate.setDate(newDate.getDate() + (direction === 'next' ? 7 : -7));
    setCurrentDate(newDate);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Court Calendar</h1>
          <p className="text-gray-600">View and manage hearing schedules</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex rounded-md shadow-sm">
            <button
              onClick={() => setView('day')}
              className={`px-4 py-2 text-sm font-medium rounded-l-md border ${
                view === 'day'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Day
            </button>
            <button
              onClick={() => setView('week')}
              className={`px-4 py-2 text-sm font-medium border-t border-b ${
                view === 'week'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Week
            </button>
            <button
              onClick={() => setView('month')}
              className={`px-4 py-2 text-sm font-medium rounded-r-md border ${
                view === 'month'
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              }`}
            >
              Month
            </button>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white shadow rounded-lg p-4">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-gray-700">Filters:</span>
          <select
            value={filters.caseType}
            onChange={(e) => setFilters({...filters, caseType: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Case Types</option>
            <option value="civil">Civil</option>
            <option value="criminal">Criminal</option>
            <option value="family">Family</option>
            <option value="tax">Tax</option>
            <option value="constitutional">Constitutional</option>
          </select>
          <select
            value={filters.urgency}
            onChange={(e) => setFilters({...filters, urgency: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Urgency Levels</option>
            <option value="habeas_corpus">Habeas Corpus</option>
            <option value="bail">Bail</option>
            <option value="injunction">Injunction</option>
            <option value="regular">Regular</option>
          </select>
          {filters.caseType || filters.urgency ? (
            <button
              onClick={() => setFilters({ caseType: '', judge: '', urgency: '' })}
              className="px-3 py-2 text-sm text-blue-600 hover:text-blue-800"
            >
              Clear Filters
            </button>
          ) : null}
        </div>
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">
            {currentDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
          </h2>
          <div className="flex space-x-2">
            <button
              onClick={() => navigateWeek('prev')}
              className="p-2 rounded-md hover:bg-gray-100"
            >
              <ChevronLeft className="h-5 w-5" />
            </button>
            <button
              onClick={() => setCurrentDate(new Date())}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Today
            </button>
            <button
              onClick={() => navigateWeek('next')}
              className="p-2 rounded-md hover:bg-gray-100"
            >
              <ChevronRight className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Capacity Legend */}
        <div className="mb-4 flex items-center gap-4 p-3 bg-gray-50 rounded-lg">
          <span className="text-sm font-medium text-gray-700">Workload Capacity:</span>
          <div className="flex items-center gap-2">
            <CheckCircle className="h-4 w-4 text-green-600" />
            <span className="text-xs text-gray-600">Light (&lt;50%)</span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-yellow-600" />
            <span className="text-xs text-gray-600">Moderate (50-80%)</span>
          </div>
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-red-600" />
            <span className="text-xs text-gray-600">Overloaded (&gt;80%)</span>
          </div>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {weekData?.data?.schedule && Object.entries(weekData.data.schedule).map(([day, data]: [string, any]) => {
              const hearingCount = data.total_hearings || 0;
              const capacity = Math.min(100, (hearingCount / 10) * 100); // Assume 10 hearings = 100% capacity
              const capacityInfo = getCapacityColor(capacity);
              const CapacityIcon = capacityInfo.icon;
              
              return (
              <div key={day} className={`border rounded-lg p-4 ${capacityInfo.bg} border-l-4 ${capacityInfo.text.replace('text-', 'border-')}`}>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <h3 className="font-medium text-gray-900">
                      {day} - {new Date(data.date).toLocaleDateString()}
                    </h3>
                    <div className={`flex items-center gap-1 px-2 py-1 rounded-full ${capacityInfo.bg} ${capacityInfo.text}`}>
                      <CapacityIcon className="h-3 w-3" />
                      <span className="text-xs font-medium">{capacityInfo.label}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-semibold text-gray-700">
                      {hearingCount} hearings
                    </span>
                    <span className="text-xs text-gray-500">
                      ({capacity.toFixed(0)}% capacity)
                    </span>
                  </div>
                </div>
                {data.is_working_day ? (
                  <div className="space-y-2">
                    {data.time_slots?.slice(0, 3).map((slot: any, idx: number) => (
                      <div key={idx}>
                        {slot.hearings.length > 0 && (
                          <div className="text-sm">
                            <span className="font-medium text-gray-700">
                              {new Date(slot.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                            <div className="ml-4 mt-1 space-y-1">
                              {slot.hearings.map((hearing: any, hIdx: number) => (
                                <div key={hIdx} className="text-gray-600">
                                  {hearing.case_number} - {hearing.courtroom}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">Weekend - No hearings</p>
                )}
              </div>
            );
            })}
          </div>
        )}
      </div>

      <div className="bg-white shadow rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Upcoming Hearings (Next 7 Days)
        </h3>
        <div className="space-y-3">
          {upcomingHearings?.data?.upcoming_hearings?.slice(0, 5).map((hearing: any) => (
            <div key={hearing.hearing_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-900">{hearing.case_number}</p>
                <p className="text-sm text-gray-600">{hearing.case_title}</p>
                <p className="text-xs text-gray-500">
                  {hearing.courtroom} • {hearing.judge}
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-medium text-gray-900">
                  {new Date(hearing.scheduled_date).toLocaleDateString()}
                </p>
                <p className="text-xs text-gray-500">
                  {new Date(hearing.scheduled_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>
            </div>
          ))}
          {(!upcomingHearings?.data?.upcoming_hearings || upcomingHearings.data.upcoming_hearings.length === 0) && (
            <p className="text-gray-500 text-center py-4">No upcoming hearings</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Calendar;