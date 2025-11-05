// Simple test apiClient export
export const apiClient = {
  getMRs: () => Promise.resolve({ success: true, data: [] }),
  getRoute: () => Promise.resolve({ success: true, data: { points: [], stats: {} } }),
  getDashboardStats: () => Promise.resolve({ success: true, data: {} }),
  getActivityFeed: () => Promise.resolve({ success: true, data: [] }),
  getMRDetail: () => Promise.resolve({ success: true, data: {} }),
  getBlueprint: () => Promise.resolve({ success: true, data: {} })
};
