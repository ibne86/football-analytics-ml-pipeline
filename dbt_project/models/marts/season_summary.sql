with matches as (

    select *
    from {{ ref('match_results') }}

),

final as (

    select
        season,
        league_id,
        league_name,
        league_country,

        count(*) as total_matches,
        sum(total_goals) as total_goals,

        sum(is_home_win) as home_wins,
        sum(is_away_win) as away_wins,
        sum(is_draw) as draws,

        round(avg(total_goals), 2) as avg_goals_per_match

    from matches

    group by
        season,
        league_id,
        league_name,
        league_country

)

select *
from final