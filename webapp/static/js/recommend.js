import React from 'react';
import ReactDOM from 'react-dom';
import $ from 'jquery';
import _ from 'underscore';

const rec_headlines = {
  'random': 'Recommendations (chosen at random)',
  'lda': 'Recommendations by text analysis',
  'collab': 'Recommendations based on your likes'
}

function ActCard(props) {
  const { act_data } = props;
  const fontSize = act_data.name.length > 50 ? '.75em' : '1em';
  return (
    <div className="act_card">
      <header onClick={props.expand_act(act_data)} style={{ fontSize }}>
        <h4><div>{act_data.name}</div></h4>
      </header>
      <div className="description">
        <div className="inner">
          <p>{act_data.description}</p>
        </div>
      </div>
    </div>
  );
}


function Act(props) {
  const { act_data } = props;
  const fontSize = act_data.name.length > 50 ? '1.25em' : '1.5em';
  return (
    <div className="act">
      <header>
        <h2 style={{ fontSize }}><div>{act_data.name}</div></h2>
      </header>
      <div className="description">
        <figure className="love_button" onClick={props.love_act}>
          <img
            src={props.is_loved ? '/static/img/symbol-color.png' : 'static/img/symbol-grey.png'}
            onClick={props.love_act}
          />
        </figure>
        {act_data.description.split('\n\r').map((p, i) => (
          <p key={i}>{p}</p>
        ))}
      </div>
      <div className="link">
        <a target="_blank" href={`https://www.billionacts.org/act/${act_data.projectID}`}>
          See on billionacts.org
        </a>
      </div>
    </div>
  );
}

function RecommenderChoices (props) {
  const liked_projectIDs = props.likes.map((act) => act.projectID);
  const likes = JSON.stringify(liked_projectIDs);
  return (
    <div className="recommender_choices">
      <form
        method="POST"
        action="/recommend/lda"
        onSubmit={props.get_recommendations}
      >
        {props.user && (
          <input type="hidden" name="googleID" value={user.id} />
        )}
        <input type="hidden" name="likes" value={likes} />
        <input type="hidden" name="description" value={props.description} />
        <button type="submit">Find acts with similar text</button>
      </form>

      <form
        method="POST"
        action="/recommend/collab"
        onSubmit={props.get_recommendations}
      >
        {props.user && (
          <input type="hidden" name="googleID" value={user.id} />
        )}
        <input type="hidden" name="likes" value={likes} />
        <input type="hidden" name="projectID" value={props.projectID} />
        <input type="hidden" name="description" value={props.description} />
        <button type="submit">Find acts based on your likes</button>
      </form>
    </div>
  );
}

class ActList extends React.Component {
  constructor (props) {
    super(props);

    let likes = [];
    if (props.user && props.user.likes.length > 0) {
      likes = props.user.likes;
    }
    this.state = {
      current_act: null,
      recommendations: [],
      likes: likes,
      last_recommendation_engine: ''
    };

    this.get_recommendations = this.get_recommendations.bind(this);
    this.fetch_projects = this.fetch_projects.bind(this);
    this.expand_act = this.expand_act.bind(this);
    this.like_act = this.like_act.bind(this);

    this._liked_act_index = (act_data) => _.findIndex(
      this.state.likes,
      (act) => act.projectID === act_data.projectID
    );
  }

  componentWillMount () {
    this.get_recommendations(false, '/recommend/random');
  }

  like_act (act_data) {
    return (event) => {
      const act_index = this._liked_act_index(act_data);
      const likes = this.state.likes.slice();
      if (act_index === -1) {
        likes.push(act_data);
      } else {
        likes.splice(act_index, 1);
      }
      this.setState({ likes });
    };
  }

  get_recommendations (event, url) {
    let data;
    if (event) {
      // If event is undefined, get_recommendations was called from
      // constructor to populate the act list randomly.
      event.preventDefault();
      url = event.target.action;
      data = $(event.target).serialize()
    }
    this.setState({
      last_recommendation_engine: url.split('/recommend/')[1],
      recommendations: []
    }, function () {
      $.ajax({
        url: url,
        method: 'POST',
        dataType: 'json',
        data: data,
        success: this.fetch_projects,
        error: (jqXHR, status, err) => {
          console.log('Getting recommendations:', jqXHR.responseText);
        },
      });
    });
  }

  fetch_projects (projectIDs) {
    if (!projectIDs) {
      console.log('No results');
      return;
    }
    const recommendations = [];
    for (var i = 0; i < projectIDs.length; i++) {
      const projectID = projectIDs[i];
      $.ajax({
        url: `/act/${projectID}`,
        method: 'GET',
        dataType: 'json',
        success: (data) => {
          recommendations.push(data);
          this.setState({ recommendations });
        },
        error: (jqXHR, status, err) => {
          console.log('Fetching projects:', jqXHR.responseText);
        },
      });
    }
  }

  expand_act (act_data) {
    return (event) => {
      this.setState({
        current_act: act_data
      }, () => {
        $('html, body').animate({
          scrollTop: $(this.act_el).offset().top
        }, 500);
      });
    };
  }

  render () {
    return (
      <div>
        <div ref={(el) => { this.act_el = el }}>
          {this.state.current_act && (
            <div>
              <Act
                act_data={this.state.current_act}
                is_loved={this._liked_act_index(this.state.current_act) !== -1}
                love_act={this.like_act(this.state.current_act)}
              />
              <RecommenderChoices
                get_recommendations={this.get_recommendations}
                projectID={this.state.current_act.projectID}
                description={this.state.current_act.description}
                user={user}
                likes={this.state.likes}
              />
            </div>
          )}
        </div>

        {this.state.recommendations.length > 0 && (
          <div className="results">
            <h2>{rec_headlines[this.state.last_recommendation_engine]}</h2>
            {this.state.recommendations.map((act_data, i) => (
              <ActCard
                key={i}
                act_data={act_data}
                expand_act={this.expand_act}
              />
            ))}
          </div>
        )}

        {this.state.likes.length > 0 && (
          <div className="results">
            <h2>Acts you liked</h2>
            {this.state.likes.map((act_data, i) => (
              <ActCard
                key={i}
                act_data={act_data}
                expand_act={this.expand_act}
              />
            ))}
          </div>
        )}
      </div>
    );
  }
}

function ActRecommender(props) {
  return (
    <div>
      <header className="page_header">
        <h1>Browse Acts of Peace</h1>
        <p style={{ fontSize: 'smaller' }}>
          from <a href="https://www.billionacts.org" target="_blank">1 Billion Acts of Peace</a>
        </p>
        <div className="login">
          {props.user ? (
            <span>
              {props.user.picture && (
                <img src={props.user.picture} title={props.user.email} />
              )}
              <a href="/logout">Logout</a>
            </span>
          ) : (
            <a href="/login">Login</a>
          )}
        </div>
      </header>

      <ActList user={user} />

      <footer>
        <div className="column">
          <div>
            David Keeling
          </div>
          <div>
            <a href="https://github.com/davidkeeling/basuggests" target="_blank">
              <img src="/static/img/github.png" style={{ height: "1em", verticalAlign: "middle" }} />
              <span style={{ paddingLeft: ".25em" }}>basuggests on github</span>
            </a>
          </div>
        </div>
        <div className="column">
          <div>
            <a href="http://www.peacejam.org" target="_blank">The PeaceJam Foundation</a>
          </div>
          <div>
            <a href="http://www.billionacts.org" target="_blank">1 Billion Acts of Peace</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

ReactDOM.render(
  <ActRecommender user={user} />,
  document.getElementById('app')
);
