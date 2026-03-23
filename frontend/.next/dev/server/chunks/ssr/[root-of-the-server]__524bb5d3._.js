module.exports = [
"[externals]/fs [external] (fs, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("fs", () => require("fs"));

module.exports = mod;
}),
"[externals]/stream [external] (stream, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("stream", () => require("stream"));

module.exports = mod;
}),
"[externals]/zlib [external] (zlib, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("zlib", () => require("zlib"));

module.exports = mod;
}),
"[externals]/react-dom [external] (react-dom, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("react-dom", () => require("react-dom"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/action-async-storage.external.js [external] (next/dist/server/app-render/action-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/action-async-storage.external.js", () => require("next/dist/server/app-render/action-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[project]/config/api.ts [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// API Configuration
__turbopack_context__.s([
    "API_BASE_URL",
    ()=>API_BASE_URL,
    "API_ENDPOINTS",
    ()=>API_ENDPOINTS
]);
const API_BASE_URL = ("TURBOPACK compile-time value", "http://localhost:8000") || 'http://127.0.0.1:8000';
const API_ENDPOINTS = {
    // Auth endpoints
    REGISTER: `${API_BASE_URL}/api/auth/register/`,
    LOGIN: `${API_BASE_URL}/api/auth/login/`,
    LOGOUT: `${API_BASE_URL}/api/auth/logout/`,
    VERIFY: `${API_BASE_URL}/api/auth/verify/`,
    REFRESH: `${API_BASE_URL}/api/auth/refresh/`,
    PROFILE: `${API_BASE_URL}/api/auth/profile/`,
    // Property endpoints
    PROPERTIES: `${API_BASE_URL}/api/properties/`,
    // Tenant endpoints
    TENANTS: `${API_BASE_URL}/api/tenants/`,
    // Landlord endpoints
    LANDLORD_LISTINGS: `${API_BASE_URL}/api/landlord/listings/`,
    LANDLORD_PRICING: `${API_BASE_URL}/api/landlord/pricing/`,
    LANDLORD_SCHEDULES: `${API_BASE_URL}/api/landlord/schedules/`,
    LANDLORD_HISTORY: `${API_BASE_URL}/api/landlord/history/`,
    LANDLORD_ANALYTICS: `${API_BASE_URL}/api/landlord/analytics/`,
    // Service endpoints
    SERVICE_MOVERS: `${API_BASE_URL}/api/service/movers/`,
    SERVICE_BOOKINGS: `${API_BASE_URL}/api/service/bookings/`,
    SERVICE_MAINTENANCE: `${API_BASE_URL}/api/service/maintenance/`,
    SERVICE_STORAGE: `${API_BASE_URL}/api/service/storage/`,
    SERVICE_INVENTORY: `${API_BASE_URL}/api/service/inventory/`,
    // Recommendations
    RECOMMENDATIONS: `${API_BASE_URL}/api/recommendations/`
};
}),
"[project]/services/api.ts [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "authAPI",
    ()=>authAPI,
    "landlordAPI",
    ()=>landlordAPI,
    "propertiesAPI",
    ()=>propertiesAPI,
    "serviceAPI",
    ()=>serviceAPI,
    "tenantAPI",
    ()=>tenantAPI
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/config/api.ts [ssr] (ecmascript)");
;
// Token management
const getTokens = ()=>{
    if ("TURBOPACK compile-time truthy", 1) return null;
    //TURBOPACK unreachable
    ;
    const access = undefined;
    const refresh = undefined;
};
const setTokens = (tokens)=>{
    if ("TURBOPACK compile-time truthy", 1) return;
    //TURBOPACK unreachable
    ;
};
const clearTokens = ()=>{
    if ("TURBOPACK compile-time truthy", 1) return;
    //TURBOPACK unreachable
    ;
};
// Generic API fetch function
async function apiCall(url, options = {}, includeAuth = true) {
    try {
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        // Add auth token if available
        if (includeAuth) {
            const tokens = getTokens();
            if (tokens?.access) {
                headers['Authorization'] = `Bearer ${tokens.access}`;
            }
        }
        const response = await fetch(url, {
            ...options,
            headers
        });
        const data = await response.json();
        if (!response.ok) {
            return {
                success: false,
                error: data?.detail || data?.error || 'An error occurred',
                errors: data
            };
        }
        return {
            success: true,
            data
        };
    } catch (error) {
        return {
            success: false,
            error: error instanceof Error ? error.message : 'Network error'
        };
    }
}
const authAPI = {
    register: async (userData)=>{
        const response = await apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].REGISTER, {
            method: 'POST',
            body: JSON.stringify(userData)
        }, false);
        if (response.success && response.data) {
            setTokens({
                access: response.data.access,
                refresh: response.data.refresh
            });
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response;
    },
    login: async (credentials)=>{
        const response = await apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LOGIN, {
            method: 'POST',
            body: JSON.stringify(credentials)
        }, false);
        if (response.success && response.data) {
            setTokens({
                access: response.data.access,
                refresh: response.data.refresh
            });
            localStorage.setItem('user', JSON.stringify(response.data.user));
        }
        return response;
    },
    logout: async ()=>{
        const tokens = getTokens();
        if (!tokens?.refresh) {
            clearTokens();
            return {
                success: true
            };
        }
        const response = await apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LOGOUT, {
            method: 'POST',
            body: JSON.stringify({
                refresh: tokens.refresh
            })
        }, true);
        clearTokens();
        return response;
    },
    verify: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].VERIFY, {
            method: 'GET'
        }, true);
    },
    refreshToken: async ()=>{
        const tokens = getTokens();
        if (!tokens?.refresh) {
            return {
                success: false,
                error: 'No refresh token available'
            };
        }
        const response = await apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].REFRESH, {
            method: 'POST',
            body: JSON.stringify({
                refresh: tokens.refresh
            })
        }, false);
        if (response.success && response.data?.access) {
            setTokens({
                access: response.data.access,
                refresh: tokens.refresh
            });
        }
        return response;
    },
    getProfile: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].PROFILE, {
            method: 'GET'
        }, true);
    },
    updateProfile: async (profileData)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].PROFILE, {
            method: 'PUT',
            body: JSON.stringify(profileData)
        }, true);
    },
    getCurrentUser: ()=>{
        if ("TURBOPACK compile-time truthy", 1) return null;
        //TURBOPACK unreachable
        ;
        const user = undefined;
    },
    isAuthenticated: ()=>{
        const tokens = getTokens();
        return !!tokens?.access;
    }
};
const propertiesAPI = {
    getAll: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].PROPERTIES, {
            method: 'GET'
        }, true);
    },
    create: async (propertyData)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].PROPERTIES, {
            method: 'POST',
            body: JSON.stringify(propertyData)
        }, true);
    }
};
const tenantAPI = {
    getAll: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].TENANTS, {
            method: 'GET'
        }, true);
    },
    create: async (tenantData)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].TENANTS, {
            method: 'POST',
            body: JSON.stringify(tenantData)
        }, true);
    },
    getRecommendations: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].RECOMMENDATIONS, {
            method: 'GET'
        }, true);
    }
};
const landlordAPI = {
    getListings: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_LISTINGS, {
            method: 'GET'
        }, true);
    },
    createListing: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_LISTINGS, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getPricing: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_PRICING, {
            method: 'GET'
        }, true);
    },
    updatePricing: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_PRICING, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getSchedules: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_SCHEDULES, {
            method: 'GET'
        }, true);
    },
    createSchedule: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_SCHEDULES, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getHistory: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_HISTORY, {
            method: 'GET'
        }, true);
    },
    getAnalytics: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_ANALYTICS, {
            method: 'GET'
        }, true);
    }
};
const serviceAPI = {
    getMovers: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_MOVERS, {
            method: 'GET'
        }, true);
    },
    getBookings: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_BOOKINGS, {
            method: 'GET'
        }, true);
    },
    createBooking: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_BOOKINGS, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getMaintenance: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_MAINTENANCE, {
            method: 'GET'
        }, true);
    },
    createMaintenance: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_MAINTENANCE, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getStorage: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_STORAGE, {
            method: 'GET'
        }, true);
    },
    getInventory: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_INVENTORY, {
            method: 'GET'
        }, true);
    },
    createInventory: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_INVENTORY, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    }
};
}),
"[project]/hooks/useAuth.ts [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useAuth",
    ()=>useAuth
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react [external] (react, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/services/api.ts [ssr] (ecmascript)");
;
;
const useAuth = ()=>{
    const [user, setUser] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])(null);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useState"])(null);
    // Load user on mount
    (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useEffect"])(()=>{
        const loadUser = async ()=>{
            try {
                if (__TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["authAPI"].isAuthenticated()) {
                    const currentUser = __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["authAPI"].getCurrentUser();
                    if (currentUser) {
                        setUser(currentUser);
                    }
                }
            } catch (err) {
                console.error('Failed to load user:', err);
            } finally{
                setIsLoading(false);
            }
        };
        loadUser();
    }, []);
    const login = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useCallback"])(async (username, password)=>{
        setIsLoading(true);
        setError(null);
        try {
            const response = await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["authAPI"].login({
                username,
                password
            });
            if (response.success && response.data) {
                setUser(response.data.user);
                return true;
            } else {
                setError(response.error || 'Login failed');
                return false;
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
            return false;
        } finally{
            setIsLoading(false);
        }
    }, []);
    const register = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useCallback"])(async (userData)=>{
        setIsLoading(true);
        setError(null);
        try {
            const response = await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["authAPI"].register(userData);
            if (response.success && response.data) {
                setUser(response.data.user);
            } else {
                setError(response.error || 'Registration failed');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally{
            setIsLoading(false);
        }
    }, []);
    const logout = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useCallback"])(async ()=>{
        setIsLoading(true);
        setError(null);
        try {
            await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["authAPI"].logout();
            setUser(null);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally{
            setIsLoading(false);
        }
    }, []);
    const clearError = (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["useCallback"])(()=>{
        setError(null);
    }, []);
    return {
        user,
        isLoading,
        isAuthenticated: !!user,
        error,
        login,
        register,
        logout,
        clearError
    };
};
}),
"[project]/components/ProtectedPage.tsx [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ProtectedPage",
    ()=>ProtectedPage
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react/jsx-dev-runtime [external] (react/jsx-dev-runtime, cjs)");
var __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react [external] (react, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useAuth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/hooks/useAuth.ts [ssr] (ecmascript)");
;
;
;
;
const ProtectedPage = ({ requiredRole, children })=>{
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const { user, isLoading, isAuthenticated } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useAuth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["useAuth"])();
    __TURBOPACK__imported__module__$5b$externals$5d2f$react__$5b$external$5d$__$28$react$2c$__cjs$29$__["default"].useEffect(()=>{
        if (!isLoading) {
            if (!isAuthenticated) {
                router.push('/login');
            } else if (requiredRole && user?.role !== requiredRole) {
                router.push('/');
            }
        }
    }, [
        isLoading,
        isAuthenticated,
        user,
        requiredRole,
        router
    ]);
    if (isLoading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
            className: "min-h-screen bg-gradient-to-br from-primary-900 to-primary-700 flex items-center justify-center",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                className: "flex flex-col items-center gap-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                        className: "text-2xl text-white font-semibold",
                        children: "Loading..."
                    }, void 0, false, {
                        fileName: "[project]/components/ProtectedPage.tsx",
                        lineNumber: 28,
                        columnNumber: 11
                    }, ("TURBOPACK compile-time value", void 0)),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                        className: "w-12 h-12 border-4 border-secondary-500 border-t-accent-500 rounded-full animate-spin"
                    }, void 0, false, {
                        fileName: "[project]/components/ProtectedPage.tsx",
                        lineNumber: 29,
                        columnNumber: 11
                    }, ("TURBOPACK compile-time value", void 0))
                ]
            }, void 0, true, {
                fileName: "[project]/components/ProtectedPage.tsx",
                lineNumber: 27,
                columnNumber: 9
            }, ("TURBOPACK compile-time value", void 0))
        }, void 0, false, {
            fileName: "[project]/components/ProtectedPage.tsx",
            lineNumber: 26,
            columnNumber: 7
        }, ("TURBOPACK compile-time value", void 0));
    }
    if (!isAuthenticated || requiredRole && user?.role !== requiredRole) {
        return null;
    }
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["Fragment"], {
        children: children
    }, void 0, false);
};
}),
"[project]/pages/service.tsx [ssr] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>ServiceProviderPortal
]);
var __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__ = __turbopack_context__.i("[externals]/react/jsx-dev-runtime [external] (react/jsx-dev-runtime, cjs)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$link$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/link.js [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$router$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/router.js [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ProtectedPage$2e$tsx__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ProtectedPage.tsx [ssr] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useAuth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/hooks/useAuth.ts [ssr] (ecmascript)");
'use client';
;
;
;
;
;
function ServiceProviderPortal() {
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$router$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__["useRouter"])();
    const { user, logout } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useAuth$2e$ts__$5b$ssr$5d$__$28$ecmascript$29$__["useAuth"])();
    const handleLogout = async ()=>{
        await logout();
        router.push('/login');
    };
    const services = [
        {
            title: 'Moving Services',
            description: 'Manage mover partnerships and track delivery bookings',
            icon: '📦',
            href: '/service/movers',
            gradient: 'from-blue-500 to-blue-600'
        },
        {
            title: 'Maintenance Providers',
            description: 'Handle maintenance requests and service schedules',
            icon: '🔧',
            href: '/service/maintenance',
            gradient: 'from-orange-500 to-orange-600'
        },
        {
            title: 'Warehousing & Storage',
            description: 'Manage storage units and inventory',
            icon: '🏠',
            href: '/service/warehousing',
            gradient: 'from-green-500 to-green-600'
        }
    ];
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ProtectedPage$2e$tsx__$5b$ssr$5d$__$28$ecmascript$29$__["ProtectedPage"], {
        requiredRole: "service_provider",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("main", {
            className: "min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 p-8",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                className: "max-w-6xl mx-auto",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                        className: "flex justify-between items-center mb-12",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h1", {
                                        className: "text-4xl font-bold text-slate-900 mb-2",
                                        children: "Service Provider Portal"
                                    }, void 0, false, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 49,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                                        className: "text-slate-600",
                                        children: [
                                            "Welcome back, ",
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                                className: "font-semibold text-blue-600",
                                                children: user?.first_name || 'Service Provider'
                                            }, void 0, false, {
                                                fileName: "[project]/pages/service.tsx",
                                                lineNumber: 51,
                                                columnNumber: 31
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 50,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/pages/service.tsx",
                                lineNumber: 48,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("button", {
                                onClick: handleLogout,
                                className: "px-6 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg font-medium transition",
                                children: "Sign Out"
                            }, void 0, false, {
                                fileName: "[project]/pages/service.tsx",
                                lineNumber: 54,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/pages/service.tsx",
                        lineNumber: 47,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                        className: "grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-12",
                        children: services.map((service)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$link$2e$js__$5b$ssr$5d$__$28$ecmascript$29$__["default"], {
                                href: service.href,
                                className: `bg-gradient-to-br ${service.gradient} p-8 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:scale-105 cursor-pointer text-white block`,
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                        className: "text-5xl mb-4",
                                        children: service.icon
                                    }, void 0, false, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 66,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h3", {
                                        className: "text-2xl font-bold mb-2",
                                        children: service.title
                                    }, void 0, false, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 67,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                                        className: "text-blue-100 mb-4",
                                        children: service.description
                                    }, void 0, false, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 68,
                                        columnNumber: 17
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                                        className: "flex items-center text-sm font-semibold",
                                        children: [
                                            "Manage ",
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                                className: "ml-2",
                                                children: "→"
                                            }, void 0, false, {
                                                fileName: "[project]/pages/service.tsx",
                                                lineNumber: 70,
                                                columnNumber: 26
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 69,
                                        columnNumber: 17
                                    }, this)
                                ]
                            }, service.href, true, {
                                fileName: "[project]/pages/service.tsx",
                                lineNumber: 65,
                                columnNumber: 15
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/pages/service.tsx",
                        lineNumber: 63,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("div", {
                        className: "bg-white rounded-xl shadow-md p-8",
                        children: [
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("h2", {
                                className: "text-2xl font-bold text-slate-900 mb-4",
                                children: "Service Management Hub"
                            }, void 0, false, {
                                fileName: "[project]/pages/service.tsx",
                                lineNumber: 78,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("p", {
                                className: "text-slate-600 mb-4",
                                children: "Manage all your real estate service needs in one place. Track bookings, manage partnerships, and grow your service business with FIND-RLB."
                            }, void 0, false, {
                                fileName: "[project]/pages/service.tsx",
                                lineNumber: 79,
                                columnNumber: 13
                            }, this),
                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("ul", {
                                className: "space-y-3 text-slate-700",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("li", {
                                        className: "flex items-center",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                                className: "text-green-500 font-bold mr-3",
                                                children: "✓"
                                            }, void 0, false, {
                                                fileName: "[project]/pages/service.tsx",
                                                lineNumber: 85,
                                                columnNumber: 17
                                            }, this),
                                            "Real-time booking management"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 84,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("li", {
                                        className: "flex items-center",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                                className: "text-green-500 font-bold mr-3",
                                                children: "✓"
                                            }, void 0, false, {
                                                fileName: "[project]/pages/service.tsx",
                                                lineNumber: 89,
                                                columnNumber: 17
                                            }, this),
                                            "Partner performance analytics"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 88,
                                        columnNumber: 15
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("li", {
                                        className: "flex items-center",
                                        children: [
                                            /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$externals$5d2f$react$2f$jsx$2d$dev$2d$runtime__$5b$external$5d$__$28$react$2f$jsx$2d$dev$2d$runtime$2c$__cjs$29$__["jsxDEV"])("span", {
                                                className: "text-green-500 font-bold mr-3",
                                                children: "✓"
                                            }, void 0, false, {
                                                fileName: "[project]/pages/service.tsx",
                                                lineNumber: 93,
                                                columnNumber: 17
                                            }, this),
                                            "Secure payment processing"
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/pages/service.tsx",
                                        lineNumber: 92,
                                        columnNumber: 15
                                    }, this)
                                ]
                            }, void 0, true, {
                                fileName: "[project]/pages/service.tsx",
                                lineNumber: 83,
                                columnNumber: 13
                            }, this)
                        ]
                    }, void 0, true, {
                        fileName: "[project]/pages/service.tsx",
                        lineNumber: 77,
                        columnNumber: 11
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/pages/service.tsx",
                lineNumber: 45,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/pages/service.tsx",
            lineNumber: 44,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/pages/service.tsx",
        lineNumber: 43,
        columnNumber: 5
    }, this);
}
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__524bb5d3._.js.map