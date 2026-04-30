// ErrorBoundary — keeps a single render error from blanking the whole app.
// Wrapped around each route in App.jsx so a broken view degrades to a banner
// instead of a white screen.

import { Component } from "react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error("View crashed:", error, info);
  }

  reset = () => this.setState({ error: null });

  render() {
    if (this.state.error) {
      return (
        <div className="error-boundary">
          <h2>Something rendered wrong.</h2>
          <p>
            The view threw an error before it could finish drawing. The rest
            of the app is still usable — pick another tab, or try this one
            again.
          </p>
          <pre className="error-detail">
            {String(this.state.error?.message ?? this.state.error)}
          </pre>
          <button type="button" className="error-retry" onClick={this.reset}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
