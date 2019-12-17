#compdef jira-new-issue
local ret=1 state

local args=(
    {-h,--help}'[display help message]' \
    '--test[Wether to be in Test mode or not]' \
    '--open[Wether to open automatically the web browser after creating the issue]' \
    '--summary=[Specify a summary for the issue]' \
    '--editor=[Editor to use default to $EDITOR or vim]:editor path:_path_files -/' \
    '--project=[Specify a project]' \
    '--version=[Specify a version]' \
    '--issuetype=[Specify an issuetype]:Issue type:(Bug Task Epic Story)' \
    '--component=[Specify a Component]' \
    '--priority=[Specify a priority]:Set priority:(Low Blocker Critical High Optional Medium Minor Urgent)' \
    '--assign=[Assign to someone (use "me"" for yourself)]:Assignee:(me)' \
    '--description-file=[Use this for description]:description file:_files'
)

_arguments -S $args && ret=0

return ret


# Local Variables:
# mode: shell-script
# End:
