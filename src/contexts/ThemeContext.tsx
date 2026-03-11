import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';

type ThemeMode = 'light' | 'dark';

interface ThemeContextType {
  mode: ThemeMode;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const CustomThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [mode, setMode] = useState<ThemeMode>(() => {
    // Get theme from localStorage or default to light
    const savedTheme = localStorage.getItem('theme-mode');
    return (savedTheme as ThemeMode) || 'light';
  });

  useEffect(() => {
    // Save theme preference to localStorage
    localStorage.setItem('theme-mode', mode);
  }, [mode]);

  const toggleTheme = () => {
    setMode(prevMode => prevMode === 'light' ? 'dark' : 'light');
  };

  const theme = createTheme({
    palette: {
      mode,
      primary: {
        main: '#4D2581',
        light: '#6B3A9E',
        dark: '#3A1D62',
        contrastText: '#ffffff',
      },
      secondary: {
        main: '#ED682B',
        light: '#F08A5A',
        dark: '#D45A1F',
        contrastText: '#ffffff',
      },
      background: {
        default: mode === 'light' ? '#f5f5f5' : '#121212',
        paper: mode === 'light' ? '#ffffff' : '#1e1e1e',
      },
      text: {
        primary: mode === 'light' ? '#1a1a1a' : '#ffffff',
        secondary: mode === 'light' ? '#666666' : '#b0b0b0',
      },
      divider: mode === 'light' ? '#e0e0e0' : '#333333',
    },
    zIndex: {
      appBar: 1200,
      drawer: 1100,
      modal: 1300,
      snackbar: 1400,
      tooltip: 1500,
    },
    components: {
      MuiAppBar: {
        styleOverrides: {
          root: {
            backgroundColor: mode === 'light' ? '#ffffff' : '#1e1e1e',
            color: mode === 'light' ? '#1a1a1a' : '#ffffff',
            borderBottom: `1px solid ${mode === 'light' ? '#e0e0e0' : '#333333'}`,
            zIndex: 1200,
          },
        },
      },
      MuiDrawer: {
        styleOverrides: {
          paper: {
            backgroundColor: mode === 'light' ? '#ffffff' : '#1e1e1e',
            borderRight: `1px solid ${mode === 'light' ? '#e0e0e0' : '#333333'}`,
            zIndex: 1100,
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundColor: mode === 'light' ? '#ffffff' : '#1e1e1e',
            border: `1px solid ${mode === 'light' ? '#e0e0e0' : '#333333'}`,
          },
        },
      },
    },
  });

  const contextValue: ThemeContextType = {
    mode,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
};
