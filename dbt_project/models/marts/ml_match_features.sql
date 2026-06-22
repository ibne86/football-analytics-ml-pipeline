with matches as (

    select *
    from {{ ref('match_results') }}

),

final as (

    select
        match_id,
        season,
        league_id,
        league_name,
        match_date,

        home_team_id,
        home_team,
        away_team_id,
        away_team,

        home_goals,
        away_goals,
        total_goals,

        match_result,
        match_result as target_match_result,

        is_home_win,
        is_away_win,
        is_draw

    from matches

)

select *
from final
