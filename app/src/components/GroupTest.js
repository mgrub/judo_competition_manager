import React, {Component} from 'react';
// import '../App.css';
import Header from './Header';

export default class GroupTest extends Component{
    // constructor(){
    //     super();
    //     this.state = {}
    // }

    render(){
        return(
            <div>
                <Header />
                <p>Hello GroupTest!</p>
            </div>
        );
    }
}


// function ToggleButton(props) {
//   return(
//     <li>{props.key}</li>
//   );
// }

// class GroupSelect extends React.Component {

//   constructor () {
//     super();
//     this.state = {groups: null}
//   }

//   componentDidMount () {
//     // fetch groups from API
//     var xhr = new XMLHttpRequest();
//     xhr.onload = function(e) {};
//       if (xhr.readyState === 4){
//         if (xhr.status === 200){
//           var story = JSON.parse(xhr.response).story
//           this.setState({
//             story: story,
//             storyLength: story.length,
//             currentChapter: story[0]
//           })
//         } else {
//           console.error(xhr.statusText)
//         }
//       }
//     }.bind(this)xhr.onerror = function(e){
//       console.error(xhr.statusText)
//     }
//     xhr.send(null)
//     xhr.open('GET', '/tournament/1/groups';
//   }

//   render() {
    



//     let data = [];
//     fetch("/api/tournament/1/groups")
//     .then(response => response.json())
//     .then(result => data.push(result))
//     .then(data => {

//     })
//     //.then(result => console.log(result))
//     .catch(err => alert(err));
    
//     var group_buttons = [];

//     console.log(data);
//     console.log(data[0].groups);
//     var groups = data[0].groups;

//     for (var i = 0; i < groups.length; i++ ) {
//       var group = groups[i];
//       group_buttons.push(<ToggleButton key={group.id} value={group}/>);
//     };

//     return (
//       <div className="group_select">
//         <ul>{group_buttons}</ul>
//       </div>
//     );

//   };
// }