"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAuthStore } from "@/stores/authStore";

export default function UsersPage() {
  const router = useRouter();
  const { user, isAuthenticated, fetchUser, logout } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      await fetchUser();
      if (!isAuthenticated) {
        router.push("/login");
      }
    };
    initAuth();
  }, [isAuthenticated, fetchUser, router]);

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200">
        <div className="px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                Omni2
              </h1>
              <div className="hidden md:flex items-center gap-6 ml-8">
                <Link href="/dashboard" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                  Dashboard
                </Link>
                <Link href="/mcps" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                  MCPs
                </Link>
                <Link href="/users" className="text-sm font-medium text-purple-600 border-b-2 border-purple-600 pb-1">
                  Users
                </Link>
                <Link href="/analytics" className="text-sm font-medium text-gray-600 hover:text-gray-900">
                  Analytics
                </Link>
              </div>
            </div>
            <button onClick={logout} className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg">
              Logout
            </button>
          </div>
        </div>
      </nav>

      <main className="p-6 max-w-7xl mx-auto">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">User Management</h2>
          <p className="text-gray-600">Manage user accounts and permissions</p>
        </div>

        <div className="bg-white rounded-xl p-12 text-center border border-gray-200">
          <div className="text-6xl mb-4">👥</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">Coming Soon</h3>
          <p className="text-gray-600 mb-6">User management interface is under development</p>
          <Link href="/dashboard" className="inline-block px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
            Back to Dashboard
          </Link>
        </div>
      </main>
    </div>
  );
}
