from langpack import lang;
def pager(baseUrl, pagevar, total, cur):
    query_prev = query_next = cur;
    result = "<form action=\"%s\" method='GET'>"%baseUrl;
    if cur > 1:
        result += ("<a href=\"%s?%s=%d\">&lt;"+lang('Prev Page')+"</a>&nbsp;")%(baseUrl, pagevar, cur-1);
    if cur < total:
        result += ("<a href=\"%s?%s=%d\">"+lang('Next Page')+"&gt;</a>&nbsp;")%(baseUrl, pagevar, cur+1);
    inputBox = "<input type='text' name='%s' maxlength='%d' size='%d' value='%d'/>"%(pagevar, len(str(total)), len(str(total)), cur);
    result += lang('_jump_page')%(total, inputBox);
    result += "&nbsp;<input type='submit' value='"+lang('OK')+"'/>";
    result += '</form>';
    return result;
