import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { BottomNav } from './BottomNav';

export const Layout: React.FC = () => {
  return (
    <div className="min-h-screen bg-background text-on-background font-body-md antialiased flex flex-col md:flex-row pb-24 md:pb-0">
      <Sidebar />
      <Header />
      <main className="flex-grow w-full md:ml-[280px] pt-20 md:pt-20 px-4 md:px-8 pb-12 max-w-7xl mx-auto">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  );
};
