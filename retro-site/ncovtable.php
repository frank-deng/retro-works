<?php
$data=apcu_fetch('ncov_data');
if($data){
    $desc=$data['desc'];
?><table width='100%' cellspacing='0'>
    <tr>
        <th width='33%' align='center'><font face='宋体'>现存确诊人数</font></th>
        <th width='33%' align='center'><font face='宋体'>累计确诊人数</font></th>
        <th width='33%' align='center'><font face='宋体'>累计治愈人数</font></th>
    </tr>
    <tr>
        <td align='center'><font face='Times New Roman'><?=$desc['currentConfirmedCount']?></font></td>
        <td align='center'><font face='Times New Roman'><?=$desc['confirmedCount']?></font></td>
        <td align='center'><font face='Times New Roman'><?=$desc['curedCount']?></font></td>
    </tr>
    <tr>
        <th align='center'><font face='宋体'>现存无症状人数</font></th>
        <th align='center'><font face='宋体'>累计境外输入人数</font></th>
        <th align='center'><font face='宋体'>累计死亡人数</font></th>
    </tr>
    <tr>
        <td align='center'><font face='Times New Roman'><?=$desc['seriousCount']?></font></td>
        <td align='center'><font face='Times New Roman'><?=$desc['suspectedCount']?></font></td>
        <td align='center'><font face='Times New Roman'><?=$desc['deadCount']?></font></td>
    </tr>
</table><?php
}