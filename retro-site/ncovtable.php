<?php
$data=apcu_fetch('ncov_data');
if($data){
    $desc=$data['desc'];
function display_incr($val){
    $val=intval($val);
    if(0==$val){
        return '';
    }
    if($val>0){
        $val='+'.$val;
        $color='red';
    }else{
        $color='green';
    }
    return ' <font color=\''.$color.'\'>('.$val.')</font>';
}
?><table width='100%' cellspacing='0'>
    <tr>
        <th width='33%' align='center'><font face='宋体'>现存确诊人数</font></th>
        <th width='33%' align='center'><font face='宋体'>累计确诊人数</font></th>
        <th width='33%' align='center'><font face='宋体'>累计治愈人数</font></th>
    </tr>
    <tr>
        <td align='center'><font face='Times New Roman'><?=$desc['currentConfirmedCount']?><?=display_incr($desc['currentConfirmedIncr'])?></font></td>
        <td align='center'><font face='Times New Roman'><?=$desc['confirmedCount']?><?=display_incr($desc['confirmedIncr'])?></font></td>
        <td align='center'><font face='Times New Roman'><?=$desc['curedCount']?><?=display_incr($desc['curedIncr'])?></font></td>
    </tr>
    <tr>
        <th align='center'><font face='宋体'>现存无症状人数</font></th>
        <th align='center'><font face='宋体'>累计境外输入人数</font></th>
        <th align='center'><font face='宋体'>累计死亡人数</font></th>
    </tr>
    <tr>
        <td align='center'><font face='Times New Roman'><?=$desc['seriousCount']?><?=display_incr($desc['seriousIncr'])?></font></td>
        <td align='center'><font face='Times New Roman'><?=$desc['suspectedCount']?><?=display_incr($desc['suspectedIncr'])?></font></td>
        <td align='center'><font face='Times New Roman'><?=$desc['deadCount']?><?=display_incr($desc['deadIncr'])?></font></td>
    </tr>
</table><?php
}