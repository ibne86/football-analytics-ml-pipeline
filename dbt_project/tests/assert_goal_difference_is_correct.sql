select *
from {{ ref('team_performance') }}
where goal_difference != (goals_for - goals_against)