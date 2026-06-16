with team_match_rows as (

    select *
    from {{ ref('int_team_match_results') }}

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