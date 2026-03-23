(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[turbopack]/browser/dev/hmr-client/hmr-client.ts [client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

/// <reference path="../../../shared/runtime-types.d.ts" />
/// <reference path="../../runtime/base/dev-globals.d.ts" />
/// <reference path="../../runtime/base/dev-protocol.d.ts" />
/// <reference path="../../runtime/base/dev-extensions.ts" />
__turbopack_context__.s([
    "connect",
    ()=>connect,
    "setHooks",
    ()=>setHooks,
    "subscribeToUpdate",
    ()=>subscribeToUpdate
]);
function connect({ addMessageListener, sendMessage, onUpdateError = console.error }) {
    addMessageListener((msg)=>{
        switch(msg.type){
            case 'turbopack-connected':
                handleSocketConnected(sendMessage);
                break;
            default:
                try {
                    if (Array.isArray(msg.data)) {
                        for(let i = 0; i < msg.data.length; i++){
                            handleSocketMessage(msg.data[i]);
                        }
                    } else {
                        handleSocketMessage(msg.data);
                    }
                    applyAggregatedUpdates();
                } catch (e) {
                    console.warn('[Fast Refresh] performing full reload\n\n' + "Fast Refresh will perform a full reload when you edit a file that's imported by modules outside of the React rendering tree.\n" + 'You might have a file which exports a React component but also exports a value that is imported by a non-React component file.\n' + 'Consider migrating the non-React component export to a separate file and importing it into both files.\n\n' + 'It is also possible the parent component of the component you edited is a class component, which disables Fast Refresh.\n' + 'Fast Refresh requires at least one parent function component in your React tree.');
                    onUpdateError(e);
                    location.reload();
                }
                break;
        }
    });
    const queued = globalThis.TURBOPACK_CHUNK_UPDATE_LISTENERS;
    if (queued != null && !Array.isArray(queued)) {
        throw new Error('A separate HMR handler was already registered');
    }
    globalThis.TURBOPACK_CHUNK_UPDATE_LISTENERS = {
        push: ([chunkPath, callback])=>{
            subscribeToChunkUpdate(chunkPath, sendMessage, callback);
        }
    };
    if (Array.isArray(queued)) {
        for (const [chunkPath, callback] of queued){
            subscribeToChunkUpdate(chunkPath, sendMessage, callback);
        }
    }
}
const updateCallbackSets = new Map();
function sendJSON(sendMessage, message) {
    sendMessage(JSON.stringify(message));
}
function resourceKey(resource) {
    return JSON.stringify({
        path: resource.path,
        headers: resource.headers || null
    });
}
function subscribeToUpdates(sendMessage, resource) {
    sendJSON(sendMessage, {
        type: 'turbopack-subscribe',
        ...resource
    });
    return ()=>{
        sendJSON(sendMessage, {
            type: 'turbopack-unsubscribe',
            ...resource
        });
    };
}
function handleSocketConnected(sendMessage) {
    for (const key of updateCallbackSets.keys()){
        subscribeToUpdates(sendMessage, JSON.parse(key));
    }
}
// we aggregate all pending updates until the issues are resolved
const chunkListsWithPendingUpdates = new Map();
function aggregateUpdates(msg) {
    const key = resourceKey(msg.resource);
    let aggregated = chunkListsWithPendingUpdates.get(key);
    if (aggregated) {
        aggregated.instruction = mergeChunkListUpdates(aggregated.instruction, msg.instruction);
    } else {
        chunkListsWithPendingUpdates.set(key, msg);
    }
}
function applyAggregatedUpdates() {
    if (chunkListsWithPendingUpdates.size === 0) return;
    hooks.beforeRefresh();
    for (const msg of chunkListsWithPendingUpdates.values()){
        triggerUpdate(msg);
    }
    chunkListsWithPendingUpdates.clear();
    finalizeUpdate();
}
function mergeChunkListUpdates(updateA, updateB) {
    let chunks;
    if (updateA.chunks != null) {
        if (updateB.chunks == null) {
            chunks = updateA.chunks;
        } else {
            chunks = mergeChunkListChunks(updateA.chunks, updateB.chunks);
        }
    } else if (updateB.chunks != null) {
        chunks = updateB.chunks;
    }
    let merged;
    if (updateA.merged != null) {
        if (updateB.merged == null) {
            merged = updateA.merged;
        } else {
            // Since `merged` is an array of updates, we need to merge them all into
            // one, consistent update.
            // Since there can only be `EcmascriptMergeUpdates` in the array, there is
            // no need to key on the `type` field.
            let update = updateA.merged[0];
            for(let i = 1; i < updateA.merged.length; i++){
                update = mergeChunkListEcmascriptMergedUpdates(update, updateA.merged[i]);
            }
            for(let i = 0; i < updateB.merged.length; i++){
                update = mergeChunkListEcmascriptMergedUpdates(update, updateB.merged[i]);
            }
            merged = [
                update
            ];
        }
    } else if (updateB.merged != null) {
        merged = updateB.merged;
    }
    return {
        type: 'ChunkListUpdate',
        chunks,
        merged
    };
}
function mergeChunkListChunks(chunksA, chunksB) {
    const chunks = {};
    for (const [chunkPath, chunkUpdateA] of Object.entries(chunksA)){
        const chunkUpdateB = chunksB[chunkPath];
        if (chunkUpdateB != null) {
            const mergedUpdate = mergeChunkUpdates(chunkUpdateA, chunkUpdateB);
            if (mergedUpdate != null) {
                chunks[chunkPath] = mergedUpdate;
            }
        } else {
            chunks[chunkPath] = chunkUpdateA;
        }
    }
    for (const [chunkPath, chunkUpdateB] of Object.entries(chunksB)){
        if (chunks[chunkPath] == null) {
            chunks[chunkPath] = chunkUpdateB;
        }
    }
    return chunks;
}
function mergeChunkUpdates(updateA, updateB) {
    if (updateA.type === 'added' && updateB.type === 'deleted' || updateA.type === 'deleted' && updateB.type === 'added') {
        return undefined;
    }
    if (updateA.type === 'partial') {
        invariant(updateA.instruction, 'Partial updates are unsupported');
    }
    if (updateB.type === 'partial') {
        invariant(updateB.instruction, 'Partial updates are unsupported');
    }
    return undefined;
}
function mergeChunkListEcmascriptMergedUpdates(mergedA, mergedB) {
    const entries = mergeEcmascriptChunkEntries(mergedA.entries, mergedB.entries);
    const chunks = mergeEcmascriptChunksUpdates(mergedA.chunks, mergedB.chunks);
    return {
        type: 'EcmascriptMergedUpdate',
        entries,
        chunks
    };
}
function mergeEcmascriptChunkEntries(entriesA, entriesB) {
    return {
        ...entriesA,
        ...entriesB
    };
}
function mergeEcmascriptChunksUpdates(chunksA, chunksB) {
    if (chunksA == null) {
        return chunksB;
    }
    if (chunksB == null) {
        return chunksA;
    }
    const chunks = {};
    for (const [chunkPath, chunkUpdateA] of Object.entries(chunksA)){
        const chunkUpdateB = chunksB[chunkPath];
        if (chunkUpdateB != null) {
            const mergedUpdate = mergeEcmascriptChunkUpdates(chunkUpdateA, chunkUpdateB);
            if (mergedUpdate != null) {
                chunks[chunkPath] = mergedUpdate;
            }
        } else {
            chunks[chunkPath] = chunkUpdateA;
        }
    }
    for (const [chunkPath, chunkUpdateB] of Object.entries(chunksB)){
        if (chunks[chunkPath] == null) {
            chunks[chunkPath] = chunkUpdateB;
        }
    }
    if (Object.keys(chunks).length === 0) {
        return undefined;
    }
    return chunks;
}
function mergeEcmascriptChunkUpdates(updateA, updateB) {
    if (updateA.type === 'added' && updateB.type === 'deleted') {
        // These two completely cancel each other out.
        return undefined;
    }
    if (updateA.type === 'deleted' && updateB.type === 'added') {
        const added = [];
        const deleted = [];
        const deletedModules = new Set(updateA.modules ?? []);
        const addedModules = new Set(updateB.modules ?? []);
        for (const moduleId of addedModules){
            if (!deletedModules.has(moduleId)) {
                added.push(moduleId);
            }
        }
        for (const moduleId of deletedModules){
            if (!addedModules.has(moduleId)) {
                deleted.push(moduleId);
            }
        }
        if (added.length === 0 && deleted.length === 0) {
            return undefined;
        }
        return {
            type: 'partial',
            added,
            deleted
        };
    }
    if (updateA.type === 'partial' && updateB.type === 'partial') {
        const added = new Set([
            ...updateA.added ?? [],
            ...updateB.added ?? []
        ]);
        const deleted = new Set([
            ...updateA.deleted ?? [],
            ...updateB.deleted ?? []
        ]);
        if (updateB.added != null) {
            for (const moduleId of updateB.added){
                deleted.delete(moduleId);
            }
        }
        if (updateB.deleted != null) {
            for (const moduleId of updateB.deleted){
                added.delete(moduleId);
            }
        }
        return {
            type: 'partial',
            added: [
                ...added
            ],
            deleted: [
                ...deleted
            ]
        };
    }
    if (updateA.type === 'added' && updateB.type === 'partial') {
        const modules = new Set([
            ...updateA.modules ?? [],
            ...updateB.added ?? []
        ]);
        for (const moduleId of updateB.deleted ?? []){
            modules.delete(moduleId);
        }
        return {
            type: 'added',
            modules: [
                ...modules
            ]
        };
    }
    if (updateA.type === 'partial' && updateB.type === 'deleted') {
        // We could eagerly return `updateB` here, but this would potentially be
        // incorrect if `updateA` has added modules.
        const modules = new Set(updateB.modules ?? []);
        if (updateA.added != null) {
            for (const moduleId of updateA.added){
                modules.delete(moduleId);
            }
        }
        return {
            type: 'deleted',
            modules: [
                ...modules
            ]
        };
    }
    // Any other update combination is invalid.
    return undefined;
}
function invariant(_, message) {
    throw new Error(`Invariant: ${message}`);
}
const CRITICAL = [
    'bug',
    'error',
    'fatal'
];
function compareByList(list, a, b) {
    const aI = list.indexOf(a) + 1 || list.length;
    const bI = list.indexOf(b) + 1 || list.length;
    return aI - bI;
}
const chunksWithIssues = new Map();
function emitIssues() {
    const issues = [];
    const deduplicationSet = new Set();
    for (const [_, chunkIssues] of chunksWithIssues){
        for (const chunkIssue of chunkIssues){
            if (deduplicationSet.has(chunkIssue.formatted)) continue;
            issues.push(chunkIssue);
            deduplicationSet.add(chunkIssue.formatted);
        }
    }
    sortIssues(issues);
    hooks.issues(issues);
}
function handleIssues(msg) {
    const key = resourceKey(msg.resource);
    let hasCriticalIssues = false;
    for (const issue of msg.issues){
        if (CRITICAL.includes(issue.severity)) {
            hasCriticalIssues = true;
        }
    }
    if (msg.issues.length > 0) {
        chunksWithIssues.set(key, msg.issues);
    } else if (chunksWithIssues.has(key)) {
        chunksWithIssues.delete(key);
    }
    emitIssues();
    return hasCriticalIssues;
}
const SEVERITY_ORDER = [
    'bug',
    'fatal',
    'error',
    'warning',
    'info',
    'log'
];
const CATEGORY_ORDER = [
    'parse',
    'resolve',
    'code generation',
    'rendering',
    'typescript',
    'other'
];
function sortIssues(issues) {
    issues.sort((a, b)=>{
        const first = compareByList(SEVERITY_ORDER, a.severity, b.severity);
        if (first !== 0) return first;
        return compareByList(CATEGORY_ORDER, a.category, b.category);
    });
}
const hooks = {
    beforeRefresh: ()=>{},
    refresh: ()=>{},
    buildOk: ()=>{},
    issues: (_issues)=>{}
};
function setHooks(newHooks) {
    Object.assign(hooks, newHooks);
}
function handleSocketMessage(msg) {
    sortIssues(msg.issues);
    handleIssues(msg);
    switch(msg.type){
        case 'issues':
            break;
        case 'partial':
            // aggregate updates
            aggregateUpdates(msg);
            break;
        default:
            // run single update
            const runHooks = chunkListsWithPendingUpdates.size === 0;
            if (runHooks) hooks.beforeRefresh();
            triggerUpdate(msg);
            if (runHooks) finalizeUpdate();
            break;
    }
}
function finalizeUpdate() {
    hooks.refresh();
    hooks.buildOk();
    // This is used by the Next.js integration test suite to notify it when HMR
    // updates have been completed.
    // TODO: Only run this in test environments (gate by `process.env.__NEXT_TEST_MODE`)
    if (globalThis.__NEXT_HMR_CB) {
        globalThis.__NEXT_HMR_CB();
        globalThis.__NEXT_HMR_CB = null;
    }
}
function subscribeToChunkUpdate(chunkListPath, sendMessage, callback) {
    return subscribeToUpdate({
        path: chunkListPath
    }, sendMessage, callback);
}
function subscribeToUpdate(resource, sendMessage, callback) {
    const key = resourceKey(resource);
    let callbackSet;
    const existingCallbackSet = updateCallbackSets.get(key);
    if (!existingCallbackSet) {
        callbackSet = {
            callbacks: new Set([
                callback
            ]),
            unsubscribe: subscribeToUpdates(sendMessage, resource)
        };
        updateCallbackSets.set(key, callbackSet);
    } else {
        existingCallbackSet.callbacks.add(callback);
        callbackSet = existingCallbackSet;
    }
    return ()=>{
        callbackSet.callbacks.delete(callback);
        if (callbackSet.callbacks.size === 0) {
            callbackSet.unsubscribe();
            updateCallbackSets.delete(key);
        }
    };
}
function triggerUpdate(msg) {
    const key = resourceKey(msg.resource);
    const callbackSet = updateCallbackSets.get(key);
    if (!callbackSet) {
        return;
    }
    for (const callback of callbackSet.callbacks){
        callback(msg);
    }
    if (msg.type === 'notFound') {
        // This indicates that the resource which we subscribed to either does not exist or
        // has been deleted. In either case, we should clear all update callbacks, so if a
        // new subscription is created for the same resource, it will send a new "subscribe"
        // message to the server.
        // No need to send an "unsubscribe" message to the server, it will have already
        // dropped the update stream before sending the "notFound" message.
        updateCallbackSets.delete(key);
    }
}
}),
"[project]/config/api.ts [client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

// API Configuration
__turbopack_context__.s([
    "API_BASE_URL",
    ()=>API_BASE_URL,
    "API_ENDPOINTS",
    ()=>API_ENDPOINTS
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$dist$2f$build$2f$polyfills$2f$process$2e$js__$5b$client$5d$__$28$ecmascript$29$__ = /*#__PURE__*/ __turbopack_context__.i("[project]/node_modules/next/dist/build/polyfills/process.js [client] (ecmascript)");
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
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/services/api.ts [client] (ecmascript)", ((__turbopack_context__) => {
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
var __TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/config/api.ts [client] (ecmascript)");
;
// Token management
const getTokens = ()=>{
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    const access = localStorage.getItem('access_token');
    const refresh = localStorage.getItem('refresh_token');
    return access && refresh ? {
        access,
        refresh
    } : null;
};
const setTokens = (tokens)=>{
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
};
const clearTokens = ()=>{
    if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
    ;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
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
        const response = await apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].REGISTER, {
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
        const response = await apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LOGIN, {
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
        const response = await apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LOGOUT, {
            method: 'POST',
            body: JSON.stringify({
                refresh: tokens.refresh
            })
        }, true);
        clearTokens();
        return response;
    },
    verify: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].VERIFY, {
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
        const response = await apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].REFRESH, {
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
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].PROFILE, {
            method: 'GET'
        }, true);
    },
    updateProfile: async (profileData)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].PROFILE, {
            method: 'PUT',
            body: JSON.stringify(profileData)
        }, true);
    },
    getCurrentUser: ()=>{
        if ("TURBOPACK compile-time falsy", 0) //TURBOPACK unreachable
        ;
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },
    isAuthenticated: ()=>{
        const tokens = getTokens();
        return !!tokens?.access;
    }
};
const propertiesAPI = {
    getAll: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].PROPERTIES, {
            method: 'GET'
        }, true);
    },
    create: async (propertyData)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].PROPERTIES, {
            method: 'POST',
            body: JSON.stringify(propertyData)
        }, true);
    }
};
const tenantAPI = {
    getAll: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].TENANTS, {
            method: 'GET'
        }, true);
    },
    create: async (tenantData)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].TENANTS, {
            method: 'POST',
            body: JSON.stringify(tenantData)
        }, true);
    },
    getRecommendations: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].RECOMMENDATIONS, {
            method: 'GET'
        }, true);
    }
};
const landlordAPI = {
    getListings: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_LISTINGS, {
            method: 'GET'
        }, true);
    },
    createListing: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_LISTINGS, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getPricing: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_PRICING, {
            method: 'GET'
        }, true);
    },
    updatePricing: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_PRICING, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getSchedules: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_SCHEDULES, {
            method: 'GET'
        }, true);
    },
    createSchedule: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_SCHEDULES, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getHistory: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_HISTORY, {
            method: 'GET'
        }, true);
    },
    getAnalytics: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].LANDLORD_ANALYTICS, {
            method: 'GET'
        }, true);
    }
};
const serviceAPI = {
    getMovers: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_MOVERS, {
            method: 'GET'
        }, true);
    },
    getBookings: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_BOOKINGS, {
            method: 'GET'
        }, true);
    },
    createBooking: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_BOOKINGS, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getMaintenance: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_MAINTENANCE, {
            method: 'GET'
        }, true);
    },
    createMaintenance: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_MAINTENANCE, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    },
    getStorage: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_STORAGE, {
            method: 'GET'
        }, true);
    },
    getInventory: async ()=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_INVENTORY, {
            method: 'GET'
        }, true);
    },
    createInventory: async (data)=>{
        return apiCall(__TURBOPACK__imported__module__$5b$project$5d2f$config$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["API_ENDPOINTS"].SERVICE_INVENTORY, {
            method: 'POST',
            body: JSON.stringify(data)
        }, true);
    }
};
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/hooks/useAuth.ts [client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "useAuth",
    ()=>useAuth
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react/index.js [client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/services/api.ts [client] (ecmascript)");
var _s = __turbopack_context__.k.signature();
;
;
const useAuth = ()=>{
    _s();
    const [user, setUser] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useState"])(null);
    const [isLoading, setIsLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useState"])(true);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useState"])(null);
    // Load user on mount
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "useAuth.useEffect": ()=>{
            const loadUser = {
                "useAuth.useEffect.loadUser": async ()=>{
                    try {
                        if (__TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["authAPI"].isAuthenticated()) {
                            const currentUser = __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["authAPI"].getCurrentUser();
                            if (currentUser) {
                                setUser(currentUser);
                            }
                        }
                    } catch (err) {
                        console.error('Failed to load user:', err);
                    } finally{
                        setIsLoading(false);
                    }
                }
            }["useAuth.useEffect.loadUser"];
            loadUser();
        }
    }["useAuth.useEffect"], []);
    const login = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuth.useCallback[login]": async (username, password)=>{
            setIsLoading(true);
            setError(null);
            try {
                const response = await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["authAPI"].login({
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
        }
    }["useAuth.useCallback[login]"], []);
    const register = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuth.useCallback[register]": async (userData)=>{
            setIsLoading(true);
            setError(null);
            try {
                const response = await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["authAPI"].register(userData);
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
        }
    }["useAuth.useCallback[register]"], []);
    const logout = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuth.useCallback[logout]": async ()=>{
            setIsLoading(true);
            setError(null);
            try {
                await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["authAPI"].logout();
                setUser(null);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'An error occurred');
            } finally{
                setIsLoading(false);
            }
        }
    }["useAuth.useCallback[logout]"], []);
    const clearError = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useCallback"])({
        "useAuth.useCallback[clearError]": ()=>{
            setError(null);
        }
    }["useAuth.useCallback[clearError]"], []);
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
_s(useAuth, "ONDWMBso78FhGF3OirL13k2xZVQ=");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/components/ProtectedPage.tsx [client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "ProtectedPage",
    ()=>ProtectedPage
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react/jsx-dev-runtime.js [client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react/index.js [client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/next/navigation.js [client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useAuth$2e$ts__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/hooks/useAuth.ts [client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
;
;
;
const ProtectedPage = ({ requiredRole, children })=>{
    _s();
    const router = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useRouter"])();
    const { user, isLoading, isAuthenticated } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useAuth$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["useAuth"])();
    __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["default"].useEffect({
        "ProtectedPage.useEffect": ()=>{
            if (!isLoading) {
                if (!isAuthenticated) {
                    router.push('/login');
                } else if (requiredRole && user?.role !== requiredRole) {
                    router.push('/');
                }
            }
        }
    }["ProtectedPage.useEffect"], [
        isLoading,
        isAuthenticated,
        user,
        requiredRole,
        router
    ]);
    if (isLoading) {
        return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "min-h-screen bg-gradient-to-br from-primary-900 to-primary-700 flex items-center justify-center",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "flex flex-col items-center gap-4",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "text-2xl text-white font-semibold",
                        children: "Loading..."
                    }, void 0, false, {
                        fileName: "[project]/components/ProtectedPage.tsx",
                        lineNumber: 28,
                        columnNumber: 11
                    }, ("TURBOPACK compile-time value", void 0)),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
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
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["Fragment"], {
        children: children
    }, void 0, false);
};
_s(ProtectedPage, "I7CmQDRNjaU3Q9z91PvBRS0PZYo=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$next$2f$navigation$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useRouter"],
        __TURBOPACK__imported__module__$5b$project$5d2f$hooks$2f$useAuth$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["useAuth"]
    ];
});
_c = ProtectedPage;
var _c;
__turbopack_context__.k.register(_c, "ProtectedPage");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/pages/tenant/search.tsx [client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>PropertySearch
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react/jsx-dev-runtime.js [client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/node_modules/react/index.js [client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/services/api.ts [client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ProtectedPage$2e$tsx__$5b$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/components/ProtectedPage.tsx [client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
'use client';
;
;
;
function PropertySearch() {
    _s();
    const [query, setQuery] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useState"])('');
    const [results, setResults] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useState"])([]);
    const [loading, setLoading] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const [error, setError] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useState"])('');
    // Load properties (and attempt personalized recommendations) on mount
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$index$2e$js__$5b$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "PropertySearch.useEffect": ()=>{
            loadRecommendations();
        }
    }["PropertySearch.useEffect"], []);
    const loadProperties = async ()=>{
        setLoading(true);
        setError('');
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["propertiesAPI"].getAll();
        if (response.success && response.data) {
            setResults(response.data);
        } else {
            setError(response.error || 'Failed to load properties');
        }
        setLoading(false);
    };
    const loadRecommendations = async ()=>{
        setLoading(true);
        setError('');
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["tenantAPI"].getRecommendations();
        if (response.success && Array.isArray(response.data?.recommended)) {
            setResults(response.data.recommended);
        } else {
            // Fallback to generic property list
            await loadProperties();
        }
        setLoading(false);
    };
    const handleSearch = async (e)=>{
        e.preventDefault();
        setLoading(true);
        setError('');
        // Fetch properties and filter based on query
        const response = await __TURBOPACK__imported__module__$5b$project$5d2f$services$2f$api$2e$ts__$5b$client$5d$__$28$ecmascript$29$__["propertiesAPI"].getAll();
        if (response.success && response.data) {
            const filtered = response.data.filter((p)=>p.location && p.location.toLowerCase().includes(query.toLowerCase()) || p.title && p.title.toLowerCase().includes(query.toLowerCase()));
            setResults(filtered);
        } else {
            setError(response.error || 'Search failed');
        }
        setLoading(false);
    };
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$components$2f$ProtectedPage$2e$tsx__$5b$client$5d$__$28$ecmascript$29$__["ProtectedPage"], {
        requiredRole: "tenant",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
            className: "min-h-screen bg-gradient-to-br from-[#e6e2d3] via-[#b3c6e7] to-[#23272b] p-8",
            children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                className: "max-w-4xl mx-auto",
                children: [
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h2", {
                        className: "text-4xl font-extrabold text-[#23272b] mb-2 tracking-tight",
                        style: {
                            color: '#23272b'
                        },
                        children: "Property Search"
                    }, void 0, false, {
                        fileName: "[project]/pages/tenant/search.tsx",
                        lineNumber: 69,
                        columnNumber: 11
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                        className: "text-lg text-[#6c7a89] mb-8",
                        children: "AI-powered property discovery"
                    }, void 0, false, {
                        fileName: "[project]/pages/tenant/search.tsx",
                        lineNumber: 70,
                        columnNumber: 11
                    }, this),
                    error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "bg-red-50 border border-red-200 rounded-lg p-4 mb-6",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-red-800",
                            children: error
                        }, void 0, false, {
                            fileName: "[project]/pages/tenant/search.tsx",
                            lineNumber: 74,
                            columnNumber: 15
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/pages/tenant/search.tsx",
                        lineNumber: 73,
                        columnNumber: 13
                    }, this),
                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("form", {
                        onSubmit: handleSearch,
                        className: "mb-8",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                            className: "flex gap-4",
                            children: [
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("input", {
                                    type: "text",
                                    placeholder: "Search by location, price, type...",
                                    value: query,
                                    onChange: (e)=>setQuery(e.target.value),
                                    className: "flex-1 px-4 py-3 border border-[#b3c6e7] bg-[#f8fafc] text-[#23272b] rounded-lg focus:ring-2 focus:ring-[#5bc0eb] focus:border-transparent shadow-sm"
                                }, void 0, false, {
                                    fileName: "[project]/pages/tenant/search.tsx",
                                    lineNumber: 80,
                                    columnNumber: 15
                                }, this),
                                /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                    type: "submit",
                                    disabled: loading,
                                    className: "px-6 py-3 bg-gradient-to-r from-[#e6e2d3] via-[#5bc0eb] to-[#23272b] text-white font-semibold rounded-lg shadow-lg hover:from-[#f7ca18] hover:to-[#5bc0eb] transition disabled:opacity-50 border border-[#b3c6e7]",
                                    children: loading ? 'Searching...' : 'Search'
                                }, void 0, false, {
                                    fileName: "[project]/pages/tenant/search.tsx",
                                    lineNumber: 87,
                                    columnNumber: 15
                                }, this)
                            ]
                        }, void 0, true, {
                            fileName: "[project]/pages/tenant/search.tsx",
                            lineNumber: 79,
                            columnNumber: 13
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/pages/tenant/search.tsx",
                        lineNumber: 78,
                        columnNumber: 11
                    }, this),
                    results.length > 0 && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "grid grid-cols-1 md:grid-cols-2 gap-8",
                        children: results.map((property)=>/*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                                className: "bg-gradient-to-br from-[#f8fafc] via-[#e6e2d3] to-[#b3c6e7] rounded-2xl shadow-xl p-6 hover:shadow-2xl transition border border-[#e6e2d3]",
                                children: [
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("h3", {
                                        className: "text-2xl font-bold text-[#23272b] mb-2",
                                        children: property.location
                                    }, void 0, false, {
                                        fileName: "[project]/pages/tenant/search.tsx",
                                        lineNumber: 101,
                                        columnNumber: 19
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                                        className: "text-[#5bc0eb] mb-4 font-semibold",
                                        children: [
                                            property.forRent && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "inline-block bg-[#e6e2d3] text-[#23272b] px-3 py-1 rounded-full text-sm mr-2 border border-[#b3c6e7]",
                                                children: [
                                                    "For Rent - $",
                                                    property.price,
                                                    "/mo"
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/pages/tenant/search.tsx",
                                                lineNumber: 105,
                                                columnNumber: 42
                                            }, this),
                                            property.forSale && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("span", {
                                                className: "inline-block bg-[#b3c6e7] text-[#23272b] px-3 py-1 rounded-full text-sm border border-[#e6e2d3]",
                                                children: [
                                                    "For Sale - $",
                                                    property.price
                                                ]
                                            }, void 0, true, {
                                                fileName: "[project]/pages/tenant/search.tsx",
                                                lineNumber: 106,
                                                columnNumber: 42
                                            }, this)
                                        ]
                                    }, void 0, true, {
                                        fileName: "[project]/pages/tenant/search.tsx",
                                        lineNumber: 104,
                                        columnNumber: 19
                                    }, this),
                                    /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("button", {
                                        className: "w-full mt-4 px-4 py-2 bg-gradient-to-r from-[#23272b] via-[#5bc0eb] to-[#e6e2d3] text-white rounded-lg font-bold shadow hover:from-[#f7ca18] hover:to-[#5bc0eb] transition",
                                        children: "View Details"
                                    }, void 0, false, {
                                        fileName: "[project]/pages/tenant/search.tsx",
                                        lineNumber: 108,
                                        columnNumber: 19
                                    }, this)
                                ]
                            }, property.propertyId || property.id, true, {
                                fileName: "[project]/pages/tenant/search.tsx",
                                lineNumber: 100,
                                columnNumber: 17
                            }, this))
                    }, void 0, false, {
                        fileName: "[project]/pages/tenant/search.tsx",
                        lineNumber: 98,
                        columnNumber: 13
                    }, this),
                    !loading && results.length === 0 && !error && /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
                        className: "text-center py-12",
                        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$node_modules$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$client$5d$__$28$ecmascript$29$__["jsxDEV"])("p", {
                            className: "text-gray-500 text-lg",
                            children: "No properties found. Try a different search."
                        }, void 0, false, {
                            fileName: "[project]/pages/tenant/search.tsx",
                            lineNumber: 118,
                            columnNumber: 15
                        }, this)
                    }, void 0, false, {
                        fileName: "[project]/pages/tenant/search.tsx",
                        lineNumber: 117,
                        columnNumber: 13
                    }, this)
                ]
            }, void 0, true, {
                fileName: "[project]/pages/tenant/search.tsx",
                lineNumber: 68,
                columnNumber: 9
            }, this)
        }, void 0, false, {
            fileName: "[project]/pages/tenant/search.tsx",
            lineNumber: 67,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/pages/tenant/search.tsx",
        lineNumber: 65,
        columnNumber: 5
    }, this);
}
_s(PropertySearch, "eZa98P27yoOezfk8ZZ7/jkjVnV8=");
_c = PropertySearch;
var _c;
__turbopack_context__.k.register(_c, "PropertySearch");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[next]/entry/page-loader.ts { PAGE => \"[project]/pages/tenant/search.tsx [client] (ecmascript)\" } [client] (ecmascript)", ((__turbopack_context__, module, exports) => {

const PAGE_PATH = "/tenant/search";
(window.__NEXT_P = window.__NEXT_P || []).push([
    PAGE_PATH,
    ()=>{
        return __turbopack_context__.r("[project]/pages/tenant/search.tsx [client] (ecmascript)");
    }
]);
// @ts-expect-error module.hot exists
if (module.hot) {
    // @ts-expect-error module.hot exists
    module.hot.dispose(function() {
        window.__NEXT_P.push([
            PAGE_PATH
        ]);
    });
}
}),
"[hmr-entry]/hmr-entry.js { ENTRY => \"[project]/pages/tenant/search.tsx\" }", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.r("[next]/entry/page-loader.ts { PAGE => \"[project]/pages/tenant/search.tsx [client] (ecmascript)\" } [client] (ecmascript)");
}),
]);

//# sourceMappingURL=%5Broot-of-the-server%5D__698b22c3._.js.map