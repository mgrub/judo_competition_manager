import React, { Component } from 'react';

import {BrowserRouter, Switch, Route} from 'react-router-dom';

import Home from './components/Home';
import GroupTest from './components/GroupTest';
import NotFound from './components/NotFound';

class App extends Component {

  render() {
    return (
      <BrowserRouter>
        <Switch>
          <Route exact path="/" component={Home} />
          <Route path="/group_test" component={GroupTest} />
          <Route component={NotFound} />
        </Switch>
      </BrowserRouter>
    );
  }
}

export default App;
