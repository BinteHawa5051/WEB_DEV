import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';
import { calendarAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';

const Calendar: React.FC = () => {
  const { user } = useAuth();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<'month' | 'week' | 'day'>('week');

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

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        ) : (
          <div className="space-y-4">
            {weekData?.data?.schedule && Object.entries(weekData.data.schedule).map(([day, data]: [string, any]) => (
              <div key={day} className="border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-medium text-gray-900">
                    {day} - {new Date(data.date).toLocaleDateString()}
                  </h3>
                  <span className="text-sm text-gray-500">
                    {data.total_hearings || 0} hearings
                  </span>
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
            ))}
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