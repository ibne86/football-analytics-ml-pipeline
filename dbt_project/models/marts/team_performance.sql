with matches as (

    select *
    from {{ ref('match_results') }}

),

team_match_rows as (

    select
        match_id,
        match_date,
        season,
        league_id,
        league_name,

        home_team_id as team_id,
        home_team as team_name,
        'Home' as home_away,

        home_goals as goals_for,
        away_goals as goals_against,

        case when match_result = 'Home Win' then 1 else 0 end as win,
        case when match_result = 'Draw' then 1 else 0 end as draw,
        case when match_result = 'Away Win' then 1 else 0 end as loss

    from matches

    union all

    select
        match_id,
        match_date,
        season,
        league_id,
        league_name,

        away_team_id as team_id,
        away_team as team_name,
        'Away' as home_away,

        away_goals as goals_for,
        home_goals as goals_against,

        case when match_result = 'Away Win' then 1 else 0 end as win,
        case when match_result = 'Draw' then 1 else 0 end as draw,
        case when match_result = 'Home Win' then 1 else 0 end as loss

    from matches

),

final as (

    select
        season,
        league_id,
        league_name,
        team_id,
        team_name,

        count(*) as matches_played,
        sum(win) as wins,
        sum(draw) as draws,
        sum(loss) as losses,

        sum(goals_for) as goals_for,
        sum(goals_against) as goals_against,
        sum(goals_for - goals_against) as goal_difference,

        sum(win * 3 + draw * 1) as points

    from team_match_rows

    group by
        season,
        league_id,
        league_name,
        team_id,
        team_name

)

select *
from final
order by points desc, goal_difference desc, goals_for desc