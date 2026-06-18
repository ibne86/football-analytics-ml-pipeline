select *
from {{ ref('team_performance') }}
where matches_played != (wins + draws + losses)