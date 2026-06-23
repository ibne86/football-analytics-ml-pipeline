with matches as (

    select *
    from {{ ref('match_results') }}

),

team_match_rows as (

    select
        match_id,
        match_datetime,
        season,
        league_id,
        home_team_id as team_id,
        home_goals as goals_for,
        away_goals as goals_against,

        case
            when match_result = 'Home Win' then 3
            when match_result = 'Draw' then 1
            else 0
        end as points

    from matches

    union all

    select
        match_id,
        match_datetime,
        season,
        league_id,
        away_team_id as team_id,
        away_goals as goals_for,
        home_goals as goals_against,

        case
            when match_result = 'Away Win' then 3
            when match_result = 'Draw' then 1
            else 0
        end as points

    from matches

),

team_pre_match_rollups as (

    select
        match_id,
        season,
        league_id,
        team_id,

        count(*) over (
            partition by season, league_id, team_id
            order by match_datetime, match_id
            rows between unbounded preceding and 1 preceding
        ) as matches_played_before,

        count(*) over (
            partition by season, league_id, team_id
            order by match_datetime, match_id
            rows between 5 preceding and 1 preceding
        ) as matches_played_last_5,

        coalesce(
            sum(points) over (
                partition by season, league_id, team_id
                order by match_datetime, match_id
                rows between unbounded preceding and 1 preceding
            ),
            0
        ) as points_before,

        coalesce(
            sum(points) over (
                partition by season, league_id, team_id
                order by match_datetime, match_id
                rows between 5 preceding and 1 preceding
            ),
            0
        ) as points_last_5,

        coalesce(
            sum(goals_for) over (
                partition by season, league_id, team_id
                order by match_datetime, match_id
                rows between 5 preceding and 1 preceding
            ),
            0
        ) as goals_for_last_5,

        coalesce(
            sum(goals_against) over (
                partition by season, league_id, team_id
                order by match_datetime, match_id
                rows between 5 preceding and 1 preceding
            ),
            0
        ) as goals_against_last_5

    from team_match_rows

),

team_pre_match_features as (

    select
        match_id,
        season,
        league_id,
        team_id,
        matches_played_before,
        points_before,
        coalesce(
            safe_divide(points_before, matches_played_before),
            0
        ) as avg_points_before,
        points_last_5,
        coalesce(
            safe_divide(points_last_5, matches_played_last_5),
            0
        ) as avg_points_last_5,
        goals_for_last_5,
        goals_against_last_5

    from team_pre_match_rollups

),

final as (

    select
        matches.match_id,
        matches.season,
        matches.league_id,
        matches.league_name,
        matches.match_date,

        matches.home_team_id,
        matches.home_team,
        matches.away_team_id,
        matches.away_team,

        home_features.matches_played_before as home_matches_played_before,
        away_features.matches_played_before as away_matches_played_before,

        home_features.points_before as home_points_before,
        away_features.points_before as away_points_before,

        home_features.avg_points_before as home_avg_points_before,
        away_features.avg_points_before as away_avg_points_before,

        home_features.points_last_5 as home_points_last_5,
        away_features.points_last_5 as away_points_last_5,

        home_features.avg_points_last_5 as home_avg_points_last_5,
        away_features.avg_points_last_5 as away_avg_points_last_5,

        home_features.goals_for_last_5 as home_goals_for_last_5,
        away_features.goals_for_last_5 as away_goals_for_last_5,

        home_features.goals_against_last_5 as home_goals_against_last_5,
        away_features.goals_against_last_5 as away_goals_against_last_5,

        matches.home_goals,
        matches.away_goals,
        matches.total_goals,

        matches.match_result,
        matches.match_result as target_match_result,

        matches.is_home_win,
        matches.is_away_win,
        matches.is_draw

    from matches

    left join team_pre_match_features as home_features
        on matches.match_id = home_features.match_id
        and matches.season = home_features.season
        and matches.league_id = home_features.league_id
        and matches.home_team_id = home_features.team_id

    left join team_pre_match_features as away_features
        on matches.match_id = away_features.match_id
        and matches.season = away_features.season
        and matches.league_id = away_features.league_id
        and matches.away_team_id = away_features.team_id

)

select *
from final
