select *
from {{ ref('team_performance') }}
where points != (wins * 3 + draws)