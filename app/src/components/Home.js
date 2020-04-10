import React, {Component} from 'react';
// import '../App.css';
import Header from './Header';

export default class Home extends Component{
    // constructor(){
    //     super();
    //     this.state = {}
    // }

    render(){
        return(
            <div>
                <Header />
                <p>Hello Home!</p>
            </div>
        );
    }
}