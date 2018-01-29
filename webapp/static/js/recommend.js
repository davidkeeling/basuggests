import React from 'react';
import $ from 'jquery';
import _ from 'underscore';
import Act from './act';
import ActCard from './act_card';

const rec_headlines = {
  'random': 'Recommendations (chosen at random)',
  'lda': 'Recommendations by text analysis',
  'collab': 'Recommendations based on your likes'
};

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
        <input type="hidden" name="projectID" value={props.projectID} />
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

export default class ActRecommender extends React.Component {
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
      recommendations: [],
      fetching_recommendations: true
    }, () => {
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
    let first_shown = false;
    for (var i = 0; i < projectIDs.length; i++) {
      const projectID = projectIDs[i];
      $.ajax({
        url: `/act/${projectID}`,
        method: 'GET',
        dataType: 'json',
        success: (data) => {
          if (!first_shown) {
            first_shown = true;
            if (this.state.last_recommendation_engine !== 'random') {
              $('html, body').animate({
                scrollTop: $('#recommendation_results').offset().top
              });
            }
            data.show_expand_hint = true;
          }
          recommendations.push(data);
          this.setState({
            recommendations,
            fetching_recommendations: false
          });
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
        });
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
                show_like_hint={this.state.likes.length === 0}
              />
              <RecommenderChoices
                get_recommendations={this.get_recommendations}
                projectID={this.state.current_act.projectID}
                description={this.state.current_act.description}
                user={this.props.user}
                likes={this.state.likes}
              />
            </div>
          )}
        </div>

        <div className="results" id="recommendation_results">
          {this.state.recommendations.length > 0 ? (
            <div>
              <h2>{rec_headlines[this.state.last_recommendation_engine]}</h2>
              {this.state.recommendations.map((act_data, i) => (
                <ActCard
                  key={i}
                  act_data={act_data}
                  expand_act={this.expand_act}
                  show_expand_hint={act_data.show_expand_hint && this.state.likes.length == 0}
                />
              ))}
            </div>
          ) : this.state.fetching_recommendations ? (
            <div style={{ height: '300px' }}>
              <h2 style={{ fontStyle: 'italic', opacity: .5 }}>Fetching recommendations...</h2>
            </div>
          ) : null}
        </div>

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
