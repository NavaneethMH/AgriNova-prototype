import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { notificationService } from '../services/api';

export const NotificationsPage: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: notifData, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => notificationService.getNotifications(1, false),
  });

  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationService.markRead(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const markAllReadMutation = useMutation({
    mutationFn: () => notificationService.markAllRead(),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const notifications = notifData?.items || [];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-headline-lg font-headline-lg text-on-surface">Notification Center</h2>
          <p className="text-body-md text-on-surface-variant">
            {notifData?.unread_count ? `${notifData.unread_count} unread alerts` : 'All alerts read'}
          </p>
        </div>

        {notifData?.unread_count ? (
          <button
            onClick={() => markAllReadMutation.mutate()}
            className="px-4 py-2 bg-surface-container hover:bg-surface-variant text-primary rounded-lg text-label-sm font-semibold transition-colors"
          >
            Mark All as Read
          </button>
        ) : null}
      </div>

      {isLoading ? (
        <div className="flex justify-center p-12">
          <span className="material-symbols-outlined text-3xl text-primary animate-spin">sync</span>
        </div>
      ) : notifications.length === 0 ? (
        <div className="bg-surface-container-lowest rounded-xl p-12 text-center border border-outline-variant/20 shadow-sm">
          <span className="material-symbols-outlined text-4xl text-outline mb-2">notifications_off</span>
          <p className="text-on-surface-variant">No notifications at this time.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {notifications.map((n) => (
            <div
              key={n.id}
              onClick={() => !n.is_read && markReadMutation.mutate(n.id)}
              className={`p-5 rounded-xl border transition-all cursor-pointer flex gap-4 items-start ${
                n.is_read
                  ? 'bg-surface-container-lowest border-outline-variant/20 opacity-75'
                  : 'bg-surface-container-lowest border-primary/40 shadow-sm ring-1 ring-primary/10'
              }`}
            >
              <div
                className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                  n.priority === 'critical'
                    ? 'bg-error-container text-on-error-container'
                    : n.priority === 'high'
                    ? 'bg-[#F59E0B]/20 text-[#B45309]'
                    : 'bg-primary-container/20 text-primary'
                }`}
              >
                <span className="material-symbols-outlined text-[20px]">
                  {n.priority === 'critical' ? 'error' : n.priority === 'high' ? 'warning' : 'notifications'}
                </span>
              </div>

              <div className="flex-grow space-y-1">
                <div className="flex justify-between items-center">
                  <h4 className={`font-semibold text-on-surface ${!n.is_read ? 'font-bold' : ''}`}>
                    {n.title}
                  </h4>
                  <span className="text-xs text-on-surface-variant">
                    {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <p className="text-body-md text-on-surface-variant text-sm">{n.message}</p>
              </div>

              {!n.is_read && <span className="w-2.5 h-2.5 rounded-full bg-primary flex-shrink-0 mt-2" />}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
