with matches as (

    select *
    from {{ ref('stg_fixtures') }}

),

final as (

    select
        match_id,
        match_datetime,
        match_date,

        league_id,
        league_name,
        league_country,
        season,
        match_round,

        home_team_id,
        home_team,
        away_team_id,
        away_team,

        home_goals,
        away_goals,
        home_goals + away_goals as total_goals,

        match_result,

        case
            when match_result = 'Home Win' then home_team
            when match_result = 'Away Win' then away_team
            when match_result = 'Draw' then 'Draw'
            else null
        end as winning_team,

        case
            when match_result = 'Home Win' then away_team
            when match_result = 'Away Win' then home_team
            when match_result = 'Draw' then 'Draw'
            else null
        end as losing_team,

        case when match_result = 'Home Win' then 1 else 0 end as is_home_win,
        case when match_result = 'Away Win' then 1 else 0 end as is_away_win,
        case when match_result = 'Draw' then 1 else 0 end as is_draw,

        venue_name,
        venue_city,
        match_status,
        match_status_short

    from matches

    where match_status_short = 'FT'

)

select *
from final