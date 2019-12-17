#compdef jira-new-issue
local ret=1 state

(( $+functions[_jira-new-issue_cache_policy] )) ||
_jira-new-issue_cache_policy () {
  typeset -a old

  # cache is valid for 1d
  old=( "$1"(md+1) )
  (( $#old ))
}


local args=(
    {-h,--help}'[display help message]' \
    '--test[Wether to be in Test mode or not]' \
    '--open[Wether to open automatically the web browser after creating the issue]' \
    '--summary=[Specify a summary for the issue]' \
    '--editor=[Editor to use default to $EDITOR or vim]:editor path:_path_files -/' \
    '--project=[Specify a project]:get project:->project' \
    '--version=[Specify a version]:complete version:->version' \
    '--issuetype=[Specify an issuetype]:Issue type:(Bug Task Epic Story)' \
    '--component=[Specify a Component]:Specify a component:->component' \
    '--priority=[Specify a priority]:Set priority:(Low Blocker Critical High Optional Medium Minor Urgent)' \
    '--assign=[Assign to someone (use "me"" for yourself)]:Assignee:(me)' \
    '--description-file=[Use this for description]:description file:_files'
)

_arguments -S $args && ret=0

case $state in
    component|project|version)
        local extra
        local cacheid=jira-${state}

        if [[ ${state} != 'project' ]];then
            for (( i = 1; i <= $#words - 1; i++ )); do
                if [[ $words[$i] == --project=*  ]]; then
                    extra=$words[$i]
                    cacheid=${cacheid}-${extra#*=}
                fi
            done
        fi

        zstyle ":completion:${curcontext}:" cache-policy _jira-new-issue_cache_policy
        if _cache_invalid "$cacheid" || ! _retrieve_cache "$cacheid";then
            local completions=(${(@f)$(command jira-new-issue ${extra} --complete=${state})})
            _store_cache "$cacheid" completions
        fi
        _describe "all ${state}s" completions && ret=0
    ;;
esac

return ret

# Local Variables:
# mode: shell-script
# End:
