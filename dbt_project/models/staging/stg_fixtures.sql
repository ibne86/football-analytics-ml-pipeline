with source as (

    select *
    from {{ source('football_raw', 'raw_fixtures') }}

),

cleaned as (

    select
        safe_cast(fixture.id as int64) as match_id,
        safe_cast(fixture.date as timestamp) as match_datetime,
        date(safe_cast(fixture.date as timestamp)) as match_date,

        safe_cast(league.id as int64) as league_id,
        league.name as league_name,
        league.country as league_country,
        safe_cast(league.season as int64) as season,
        league.round as match_round,

        safe_cast(teams.home.id as int64) as home_team_id,
        teams.home.name as home_team,

        safe_cast(teams.away.id as int64) as away_team_id,
        teams.away.name as away_team,

        safe_cast(goals.home as int64) as home_goals,
        safe_cast(goals.away as int64) as away_goals,

        fixture.status.long as match_status,
        fixture.status.short as match_status_short,

        fixture.venue.name as venue_name,
        fixture.venue.city as venue_city

    from source

),

final as (

    select
        *,

        case
            when home_goals is null or away_goals is null then null
            when home_goals > away_goals then 'Home Win'
            when away_goals > home_goals then 'Away Win'
            else 'Draw'
        end as match_result,

        home_goals + away_goals as total_goals,

        case
            when match_status_short = 'FT' then true
            else false
        end as is_finished

    from cleaned

)

select *
from final