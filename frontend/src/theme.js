import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: "#1d4ed8",
      dark: "#1e3a8a",
    },
    secondary: {
      main: "#0f766e",
    },
    warning: {
      main: "#b45309",
    },
    background: {
      default: "#f6f7f9",
      paper: "#ffffff",
    },
    text: {
      primary: "#111827",
      secondary: "#5b6472",
    },
  },
  typography: {
    fontFamily: "'Inter', 'Arial', sans-serif",
    h1: {
      fontSize: "1.55rem",
      fontWeight: 800,
      letterSpacing: 0,
    },
    h2: {
      fontSize: "1.1rem",
      fontWeight: 800,
      letterSpacing: 0,
    },
    h3: {
      fontSize: "1rem",
      fontWeight: 700,
      letterSpacing: 0,
    },
    button: {
      fontWeight: 700,
      textTransform: "none",
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          minHeight: 42,
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        size: "small",
      },
    },
  },
});

