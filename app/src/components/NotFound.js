import React, {Component} from 'react';
// import '../App.css';
import Header from './Header';

export default class NotFound extends Component{

    render(){
        return(
            <div>
                <Header />
                <p>Ups, the URL you specified could not be resolved. :-( </p>
            </div>
        );
    }
}