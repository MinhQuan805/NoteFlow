// Import functions and reducers
import { configureStore, combineReducers } from '@reduxjs/toolkit'
import counterReducer from '@/redux/counter/counterSlice'

// Import Redux Persist utilities to enable state persistence
import {
  persistReducer,
  FLUSH,
  REHYDRATE,
  PAUSE,
  PERSIST,
  PURGE,
  REGISTER,
} from 'redux-persist'
import storage from 'redux-persist/lib/storage'

// Combine all slice reducers into a single root reducer
const rootReducer = combineReducers({
  counter: counterReducer,
})

// Configuration for Redux Persist
const persistConfig = {
  key: 'root',
  version: 1,
  storage,
  whitelist: []
}

// Wrap the root reducer with persistReducer to enable persistence
const persistedReducer = persistReducer(persistConfig, rootReducer)

// Function that creates and configures the Redux store
export const makeStore = () => {
  return configureStore({
    reducer: persistedReducer,
    // Configure middleware to ignore Redux Persist's non-serializable actions
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware({
        serializableCheck: {
          ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
        },
      }),
  })
}

// TypeScript helper types
// AppStore: type of the Redux store instance
export type AppStore = ReturnType<typeof makeStore>
// RootState: type representing the global Redux state
export type RootState = ReturnType<AppStore['getState']>
// AppDispatch: type for the store's dispatch function
export type AppDispatch = AppStore['dispatch']
