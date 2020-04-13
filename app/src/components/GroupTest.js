import React, {Component} from 'react';
// import '../App.css';
import Header from './Header';
import { Button } from 'semantic-ui-react'

export default class GroupTest extends Component{
    constructor(props){
        super(props);
        this.state = {
            groups: {},
            error: null,
        }
    }

    setGroupsFromResponse(data) {
        let group_ids = data["groups"];
        var groups = {};
        for (var id of group_ids) {
            groups[id] = false;
        }
        this.setState({
            groups: groups,
        });

        console.log(this.state.groups)
    }

    componentDidMount(){
        let url = '/api/tournament/1/groups';

        fetch(url)
        .then(response => response.json())
        .then(data => this.setGroupsFromResponse(data))
        .catch(error => {
            this.setState({error:error});
        });
    }

    handleClick(event, id) {
        var currentGroups = this.state.groups;

        if ( event.ctrlKey ) {
            currentGroups[id] = !currentGroups[id];  // toggle
        } else {
            for (var key of Object.keys(currentGroups)) {
                currentGroups[key] = false;
            }
            currentGroups[id] = true;
        }
        
        console.log(currentGroups)
        this.setState({"groups": currentGroups});
    }

    render(){
        let group_ids = Object.keys(this.state.groups)
        let n_groups = group_ids.length

        return(
            <div>
                <Header />
                <div class="ui vertical buttons">
                {
                    n_groups === 0 && 
                    <p>No data fetched.</p>
                }
                {
                    n_groups > 0 &&
                        group_ids.map( (key, index) => {
                            return(<Button toggle active={this.state.groups[key]} onClick={(event) => this.handleClick(event, key)}>{key}</Button>);
                        })
                }
                </div>
                {this.state.error &&
                    <h3>{this.state.error}</h3>
                }
            </div>
        );
    }
}
