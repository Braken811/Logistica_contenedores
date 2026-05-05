
with open('dashboard.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Keep only the HTML part (before the bootstrap script)
html_part = content[:64086]

new_js = """    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        /* ═══ CONFIG & UTILS ═══ */
        const CONFIG = { API_BASE: 'http://127.0.0.1:8000', TOKEN_KEY: 'mz_auth_token' };
        const sanitizeHTML = s => typeof s === 'string' ? (DOMPurify?.sanitize(s) || s.replace(/[&<>"']/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]))) : (s ?? '—');
        const debounce = (fn, d=300) => { let t; return (...a) => { clearTimeout(t); t=setTimeout(()=>fn(...a), d); }; };
        function showToast(msg, type='success') {
            const c=document.getElementById('toastStack'), t=document.createElement('div');
            t.className=`toast ${type}`; t.setAttribute('role','alert');
            t.innerHTML=`<i class="bi bi-${type==='success'?'check-circle-fill':type==='info'?'info-circle-fill':'x-circle-fill'}"></i> ${sanitizeHTML(msg)}<div class="toast-progress"></div>`;
            c.appendChild(t); setTimeout(()=>{t.style.opacity='0';setTimeout(()=>t.remove(),300)},3500);
        }
        function getBadgeStatus(e) { return `<span class="badge-status ${e}">${e.replace(/_/g,' ')}</span>`; }
        function fmtMoney(n) { return '$'+Number(n||0).toLocaleString('es-CO'); }
        function fmtDate(d) { return d ? String(d).substring(0,10) : '—'; }

        /* ═══ AUTH ═══ */
        function getAuthToken()  { try { return localStorage.getItem(CONFIG.TOKEN_KEY); } catch(e){return null;} }
        function getAuthRole()   { try { return localStorage.getItem('mz_auth_role'); } catch(e){return null;} }
        function getAuthUser()   { try { return localStorage.getItem('mz_auth_user'); } catch(e){return null;} }
        function getAuthUserId() { try { return parseInt(localStorage.getItem('mz_auth_userid')||'0'); } catch(e){return 0;} }
        function clearAuthData() { ['mz_auth_token','mz_auth_role','mz_auth_user','mz_auth_userid'].forEach(k=>localStorage.removeItem(k)); }
        const TokenManager = {
            headers() { const t=getAuthToken(); return t?{'Authorization':`Bearer ${t}`}:{}; },
            clear()   { clearAuthData(); },
        };

        /* ═══ API CLIENT ═══ */
        const ApiClient = {
            async request(method, endpoint, body=null) {
                const headers = {'Content-Type':'application/json', ...TokenManager.headers()};
                try {
                    const res=await fetch(`${CONFIG.API_BASE}${endpoint}`,{method,headers,body:body?JSON.stringify(body):null});
                    if(!res.ok){
                        if(res.status===401){TokenManager.clear();window.location.href='/login';return;}
                        let errMsg=`Error ${res.status}`;
                        try{const eb=await res.json();errMsg=eb.detail||errMsg;}catch(e){}
                        throw new Error(errMsg);
                    }
                    if(res.status===204) return {ok:true,data:null};
                    const json=await res.json();
                    if(Array.isArray(json)) return {ok:true,data:json,meta:{total:json.length,page:1,totalPages:1}};
                    return {ok:true,data:json};
                } catch(err){ if(err.name!=='AbortError'){console.error('API Error',err);} throw err; }
            }
        };

        /* ═══ STATE ═══ */
        let currentUserRole=null, currentPage=1, rowsPerPage=10;
        let DB_TIPOS=[], DB_CLIENTES=[], DB_CONTENEDORES_API=[], DB_USUARIOS_API=[];
        let DB_ARRENDAMIENTOS_API=[], DB_FACTURACION_API=[], DB_NOTIFICACIONES=[];
        let notifLeidas = new Set(JSON.parse(localStorage.getItem('notif_leidas')||'[]'));
        let editId=null, editUserId=null, editClientId=null, editFactId=null, editRentalId=null;
        let DASH_STATS = null;

        /* ═══ ROLE & NAV ═══ */
        const NAV_CONFIG = [
            {id:'panel',title:'Panel General',icon:'bi-grid-1x2-fill',section:'principal',badge:'badgeCont'},
            {id:'contenedores',title:'Contenedores',icon:'bi-box-seam-fill',section:'principal'},
            {id:'zonas',title:'Por Zona',icon:'bi-geo-alt-fill',section:'principal'},
            {id:'movimientos',title:'Movimientos',icon:'bi-arrow-left-right',section:'principal'},
            {id:'arrendamientos',title:'Arrendamientos',icon:'bi-calendar2-week-fill',section:'gestion',badge:'badgeArr',badgeYellow:true},
            {id:'historial',title:'Historial',icon:'bi-clock-history',section:'gestion'},
            {id:'clientes',title:'Clientes',icon:'bi-people-fill',section:'sistema'},
            {id:'facturacion',title:'Facturación',icon:'bi-receipt',section:'sistema'},
            {id:'reportes',title:'Reportes',icon:'bi-bar-chart-fill',section:'sistema'},
            {id:'usuarios',title:'Usuarios',icon:'bi-shield-lock-fill',section:'sistema'}
        ];
        const PAGE_PERMS = {panel:['admin','supervisor','operador','auditor'],contenedores:['admin','supervisor','operador','auditor'],zonas:['admin','supervisor','operador','auditor'],movimientos:['admin','supervisor','operador','auditor'],arrendamientos:['admin','supervisor','auditor'],historial:['admin','supervisor','operador','auditor'],clientes:['admin','auditor'],facturacion:['admin','auditor'],reportes:['admin','supervisor','auditor'],usuarios:['admin']};
        const ACT_PERMS  = {createContainer:['admin','supervisor'],editContainer:['admin','supervisor'],deleteContainer:['admin'],exportCSV:['admin','supervisor','auditor'],createRental:['admin'],createFact:['admin'],createClient:['admin']};
        function canAccessPage(id){ return currentUserRole && PAGE_PERMS[id]?.includes(currentUserRole); }
        function canPerformAction(a){ return currentUserRole && ACT_PERMS[a]?.includes(currentUserRole); }

        function buildSidebar(){
            const nav=document.getElementById('sidebarNav');
            const sections={principal:[],gestion:[],sistema:[]};
            NAV_CONFIG.forEach(p=>{ if(canAccessPage(p.id)) sections[p.section].push(p); });
            let html='';
            for(const [sec,pages] of Object.entries(sections)){
                if(!pages.length) continue;
                html+=`<div class="nav-section-label">${sec==='principal'?'Principal':sec==='gestion'?'Gestión':'Sistema'}</div>`;
                pages.forEach(p=>{
                    const badge=p.badge?`<span class="nav-badge${p.badgeYellow?' yellow':''}" id="${p.badge}">0</span>`:'';
                    html+=`<div class="nav-item ${p.id==='panel'?'active':''}" data-page="${p.id}" onclick="navigateTo('${p.id}',this)"><i class="bi ${p.icon}"></i><span>${p.title}</span>${badge}</div>`;
                });
            }
            nav.innerHTML=html;
        }
        function applyRoleBasedUI(){
            buildSidebar();
            const show=(id,cond)=>{const el=document.getElementById(id);if(el)el.style.display=cond?'':'none';};
            show('btnNewContainer',canPerformAction('createContainer'));
            show('btnExportCont',canPerformAction('exportCSV'));
            show('btnExportMov',canPerformAction('exportCSV'));
            show('btnNewClient',canPerformAction('createClient'));
            show('btnNewFact',canPerformAction('createFact'));
            show('btnNewRental',canPerformAction('createRental'));
            show('btnExportFact',canPerformAction('exportCSV'));
        }
        function showLoader(id){const l=document.getElementById(id);if(l)l.classList.add('active');}
        function hideLoader(id){const l=document.getElementById(id);if(l)l.classList.remove('active');}

        /* ═══ DASHBOARD STATS ═══ */
        async function loadDashboardStats(){
            try{
                const res=await ApiClient.request('GET','/dashboard/stats');
                if(!res?.ok) return;
                DASH_STATS=res.data;
                const s=res.data;
                document.getElementById('kpiTotal').textContent=s.total_contenedores||0;
                document.getElementById('kpiDisp').textContent=s.por_estado?.disponible||0;
                document.getElementById('kpiTrans').textContent=s.por_estado?.en_transito||0;
                document.getElementById('kpiAlert').textContent=s.proximos_vencer||0;
                const bc=document.getElementById('badgeCont'),ba=document.getElementById('badgeArr');
                if(bc) bc.textContent=s.total_contenedores||0;
                if(ba) ba.textContent=s.proximos_vencer||0;
                updateChartsFromStats(s);
            }catch(e){console.error(e);}
        }

        /* ═══ NOTIFICATIONS ═══ */
        async function loadNotifications(){
            try{
                const res=await ApiClient.request('GET','/dashboard/notificaciones');
                if(!res?.ok) return;
                DB_NOTIFICACIONES=res.data||[];
                const noLeidas=DB_NOTIFICACIONES.filter((_,i)=>!notifLeidas.has(i)).length;
                const ct=document.getElementById('notifCount'), dt=document.getElementById('notifDot');
                if(noLeidas>0){ct.textContent=noLeidas;ct.style.display='block';dt.style.display='block';}
                else{ct.style.display='none';dt.style.display='none';}
            }catch(e){}
        }
        function toggleNotifPanel(){document.getElementById('notifPanel').classList.toggle('open');document.getElementById('notifOverlay').classList.toggle('show');if(document.getElementById('notifPanel').classList.contains('open'))buildNotifPanel();}
        function closeNotifPanel(){document.getElementById('notifPanel').classList.remove('open');document.getElementById('notifOverlay').classList.remove('show');}
        function markNotifRead(i){
            notifLeidas.add(i); localStorage.setItem('notif_leidas',JSON.stringify([...notifLeidas]));
            buildNotifPanel();
            const noLeidas=DB_NOTIFICACIONES.filter((_,idx)=>!notifLeidas.has(idx)).length;
            document.getElementById('notifBadge').textContent=noLeidas;
            const ct=document.getElementById('notifCount');
            if(noLeidas>0){ct.textContent=noLeidas;}else{ct.style.display='none';document.getElementById('notifDot').style.display='none';}
        }
        function markAllNotificationsRead(){
            DB_NOTIFICACIONES.forEach((_,i)=>notifLeidas.add(i));
            localStorage.setItem('notif_leidas',JSON.stringify([...notifLeidas]));
            document.getElementById('notifBadge').textContent='0';
            document.getElementById('notifCount').style.display='none';
            document.getElementById('notifDot').style.display='none';
            buildNotifPanel(); showToast('Todas leídas');
        }
        function buildNotifPanel(){
            const noLeidas=DB_NOTIFICACIONES.filter((_,i)=>!notifLeidas.has(i)).length;
            document.getElementById('notifBadge').textContent=noLeidas;
            if(!DB_NOTIFICACIONES.length){document.getElementById('notifBody').innerHTML='<div style="text-align:center;padding:2rem;color:var(--text-muted)">Sin notificaciones.</div>';return;}
            const html=DB_NOTIFICACIONES.map((n,i)=>{
                const leida=notifLeidas.has(i);
                const ico=n.tipo==='error'?'exclamation-triangle-fill':n.tipo==='warn'?'clock-fill':'arrow-left-right';
                return `<div class="notif-item" onclick="markNotifRead(${i})" style="cursor:pointer;${leida?'opacity:.45':''}">
                    <div class="notif-item-icon ${n.tipo}"><i class="bi bi-${ico}"></i></div>
                    <div><div class="notif-item-text"><strong>${sanitizeHTML(n.titulo)}</strong></div>
                    <div class="notif-item-text" style="font-size:.72rem">${sanitizeHTML(n.mensaje)}</div>
                    <div class="notif-item-time">${n.fecha}</div></div>
                </div>`;
            }).join('');
            document.getElementById('notifBody').innerHTML=`<div class="notif-section"><div class="notif-section-label">Notificaciones del sistema</div>${html}</div>`;
        }

        /* ═══ PROFILE PANEL ═══ */
        function openProfilePanel(){
            const user=getAuthUser(), role=getAuthRole();
            document.getElementById('profileAvatar').textContent=(user||'AD').substring(0,2).toUpperCase();
            document.getElementById('profileName').textContent=user||'Usuario';
            document.getElementById('profileRole').textContent=role||'';
            const uid=getAuthUserId();
            if(uid){ ApiClient.request('GET',`/usuarios/${uid}`).then(r=>{ if(r?.ok){document.getElementById('pNombres').value=r.data.nombres||'';document.getElementById('pApellidos').value=r.data.apellidos||'';document.getElementById('pEmail').value=r.data.email||'';} }).catch(()=>{}); }
            document.getElementById('profilePanel').classList.add('open');
            document.getElementById('profileOverlay').classList.add('show');
        }
        function closeProfilePanel(){document.getElementById('profilePanel').classList.remove('open');document.getElementById('profileOverlay').classList.remove('show');}
        async function saveProfile(){
            const uid=getAuthUserId(); if(!uid){showToast('No se pudo identificar usuario','error');return;}
            const payload={nombres:document.getElementById('pNombres').value.trim(),apellidos:document.getElementById('pApellidos').value.trim()||null,email:document.getElementById('pEmail').value.trim()||null};
            const pass=document.getElementById('pPass').value.trim(); if(pass) payload.password=pass;
            try{
                await ApiClient.request('PUT',`/usuarios/${uid}`,payload);
                document.getElementById('sidebarUser').textContent=payload.nombres||getAuthUser();
                document.getElementById('profileName').textContent=payload.nombres||getAuthUser();
                document.getElementById('pPass').value='';
                showToast('Perfil actualizado');
            }catch(e){showToast(e.message||'Error al guardar','error');}
        }

        /* ═══ REFERENCE DATA ═══ */
        async function loadReferenceData(){
            try{
                const [tr,cr]=await Promise.all([ApiClient.request('GET','/tipos-contenedores'),ApiClient.request('GET','/clientes')]);
                if(tr?.ok) DB_TIPOS=tr.data;
                if(cr?.ok) DB_CLIENTES=cr.data;
                populateModalSelects(); populateFilters();
            }catch(e){}
        }
        function populateModalSelects(){
            const mt=document.getElementById('mType'), mc=document.getElementById('mClient');
            const fc=document.getElementById('fContenedor'), rc=document.getElementById('rContenedor'), rcl=document.getElementById('rCliente');
            if(mt&&DB_TIPOS.length) mt.innerHTML=DB_TIPOS.map(t=>`<option value="${t.id_tipo}">${sanitizeHTML(t.nombre)}</option>`).join('');
            if(mc) mc.innerHTML='<option value="">— Sin cliente —</option>'+(DB_CLIENTES.length?DB_CLIENTES.map(c=>`<option value="${c.id_cliente}">${sanitizeHTML(c.nombre)}</option>`).join(''):'');
            const contOpts=DB_CONTENEDORES_API.length?DB_CONTENEDORES_API.map(c=>`<option value="${c.id_contenedor}">${sanitizeHTML(c.id_codigo)}</option>`).join(''):'';
            if(fc) fc.innerHTML=contOpts||'<option value="">Sin contenedores</option>';
            if(rc) rc.innerHTML=contOpts||'<option value="">Sin contenedores</option>';
            if(rcl) rcl.innerHTML=DB_CLIENTES.length?DB_CLIENTES.map(c=>`<option value="${c.id_cliente}">${sanitizeHTML(c.nombre)}</option>`).join(''):'<option value="">Sin clientes</option>';
        }
        function populateFilters(){
            const fc=document.getElementById('filtClient'), ft=document.getElementById('filtType');
            if(fc&&DB_CLIENTES.length) fc.innerHTML='<option value="">Todos los clientes</option>'+DB_CLIENTES.map(c=>`<option value="${c.id_cliente}">${sanitizeHTML(c.nombre)}</option>`).join('');
            if(ft&&DB_TIPOS.length) ft.innerHTML='<option value="">Todos los tipos</option>'+DB_TIPOS.map(t=>`<option value="${t.id_tipo}">${sanitizeHTML(t.nombre)}</option>`).join('');
        }

        /* ═══ CHARTS ═══ */
        let charts={}, chartsInit=false, mapInstance=null, mapInit=false;
        function applyTheme(){
            const theme=document.documentElement.getAttribute('data-bs-theme');
            Chart.defaults.color=theme==='dark'?'rgba(160,185,215,0.55)':'rgba(0,0,0,0.6)';
            Chart.defaults.borderColor=theme==='dark'?'rgba(255,255,255,0.04)':'rgba(0,0,0,0.08)';
            Chart.defaults.font.family="'DM Sans',system-ui,sans-serif";
            initCharts();
        }
        function initCharts(){
            Object.values(charts).forEach(c=>c?.destroy()); charts={}; chartsInit=false;
            const ctx=id=>document.getElementById(id)?.getContext('2d');
            if(ctx('chartMovements')) charts.mov=new Chart(ctx('chartMovements'),{type:'line',data:{labels:['Ene','Feb','Mar','Abr','May','Jun'],datasets:[{data:[0,0,0,0,0,0],borderColor:'#D32F2F',backgroundColor:'rgba(211,47,47,0.06)',fill:true,tension:.4,label:'Movimientos'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});
            if(ctx('chartTypes')) charts.typ=new Chart(ctx('chartTypes'),{type:'doughnut',data:{labels:['Sin datos'],datasets:[{data:[1],backgroundColor:['#1a2b4c']}]},options:{cutout:'68%',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}}}});
            if(ctx('chartStates')) charts.sta=new Chart(ctx('chartStates'),{type:'bar',data:{labels:['Disp','Asig','Tráns','Patio','Mant','Fuera'],datasets:[{data:[0,0,0,0,0,0],backgroundColor:['#00c896','#42a5f5','#ffca28','#ce93d8','#ffb74d','#D32F2F'],borderRadius:4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});
            if(ctx('chartClients')) charts.cli=new Chart(ctx('chartClients'),{type:'bar',data:{labels:['Sin datos'],datasets:[{data:[0],backgroundColor:'#42a5f5',borderRadius:4}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});
            if(ctx('chartRentals')) charts.ren=new Chart(ctx('chartRentals'),{type:'doughnut',data:{labels:['Activos','Por vencer'],datasets:[{data:[0,0],backgroundColor:['#00c896','#D32F2F']}]},options:{cutout:'65%',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}}}});
            chartsInit=true;
            if(DASH_STATS) updateChartsFromStats(DASH_STATS);
        }
        function updateChartsFromStats(s){
            if(!chartsInit) return;
            const estados=['disponible','asignado','en_transito','en_patio','en_mantenimiento','fuera_de_servicio'];
            if(charts.sta){charts.sta.data.datasets[0].data=estados.map(e=>s.por_estado[e]||0);charts.sta.update();}
            if(charts.typ&&Object.keys(s.por_tipo||{}).length){const lb=Object.keys(s.por_tipo),dt=Object.values(s.por_tipo);charts.typ.data.labels=lb;charts.typ.data.datasets[0].data=dt;charts.typ.data.datasets[0].backgroundColor=['#D32F2F','#42a5f5','#00c896','#ffca28','#ce93d8','#ffb74d','#1a2b4c'].slice(0,lb.length);charts.typ.update();}
            if(charts.cli&&Object.keys(s.por_cliente||{}).length){const lb=Object.keys(s.por_cliente),dt=Object.values(s.por_cliente);charts.cli.data.labels=lb;charts.cli.data.datasets[0].data=dt;charts.cli.update();}
            if(charts.ren){charts.ren.data.datasets[0].data=[s.arrendamientos_activos||0,s.proximos_vencer||0];charts.ren.update();}
        }
        function renderReportPage(s){
            if(!s) return;
            const rg=document.getElementById('reportKpiGrid'); if(!rg) return;
            rg.innerHTML=`
                <div class="kpi-card red"><div class="kpi-icon red"><i class="bi bi-box-seam-fill"></i></div><div class="kpi-value">${s.total_contenedores}</div><div class="kpi-label">Total contenedores</div></div>
                <div class="kpi-card green"><div class="kpi-icon green"><i class="bi bi-calendar2-check"></i></div><div class="kpi-value">${s.arrendamientos_activos}</div><div class="kpi-label">Arrendamientos activos</div></div>
                <div class="kpi-card blue"><div class="kpi-icon blue"><i class="bi bi-arrow-left-right"></i></div><div class="kpi-value">${s.total_movimientos}</div><div class="kpi-label">Total movimientos</div></div>
                <div class="kpi-card yellow"><div class="kpi-icon yellow"><i class="bi bi-exclamation-triangle-fill"></i></div><div class="kpi-value">${s.proximos_vencer}</div><div class="kpi-label">Alertas vencimiento</div></div>`;
            const ctx=id=>document.getElementById(id)?.getContext('2d');
            const estados=['disponible','asignado','en_transito','en_patio','en_mantenimiento','fuera_de_servicio'];
            if(ctx('chartReportStates')) new Chart(ctx('chartReportStates'),{type:'bar',data:{labels:['Disp','Asig','Tráns','Patio','Mant','Fuera'],datasets:[{data:estados.map(e=>s.por_estado[e]||0),backgroundColor:['#00c896','#42a5f5','#ffca28','#ce93d8','#ffb74d','#D32F2F'],borderRadius:4}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});
            if(ctx('chartReportTypes')&&Object.keys(s.por_tipo||{}).length){const lb=Object.keys(s.por_tipo),dt=Object.values(s.por_tipo);new Chart(ctx('chartReportTypes'),{type:'doughnut',data:{labels:lb,datasets:[{data:dt,backgroundColor:['#D32F2F','#42a5f5','#00c896','#ffca28','#ce93d8','#ffb74d','#1a2b4c'].slice(0,lb.length)}]},options:{cutout:'60%',responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'bottom',labels:{boxWidth:10,font:{size:10}}}}}});}
            if(ctx('chartReportClients')&&Object.keys(s.por_cliente||{}).length){const lb=Object.keys(s.por_cliente),dt=Object.values(s.por_cliente);new Chart(ctx('chartReportClients'),{type:'bar',data:{labels:lb,datasets:[{data:dt,backgroundColor:'#42a5f5',borderRadius:4}]},options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}});}
        }

        /* ═══ ALERTS ═══ */
        async function renderAlerts(){
            try{
                const res=await ApiClient.request('GET','/arrendamientos/proximos-vencer?dias=7');
                const items=res?.data||[];
                const today=new Date();
                document.getElementById('alertsList').innerHTML=items.length
                    ?items.map(a=>{const d=Math.ceil((new Date(a.fecha_fin)-today)/86400000);const cl=DB_CLIENTES.find(c=>c.id_cliente===a.id_cliente)?.nombre||`#${a.id_cliente}`;const co=DB_CONTENEDORES_API.find(c=>c.id_contenedor===a.id_contenedor)?.id_codigo||`#${a.id_contenedor}`;return`<div class="alert-row"><div class="alert-icon ${d<=2?'error':'warn'}"><i class="bi bi-${d<=2?'exclamation-triangle-fill':'clock-fill'}"></i></div><div><div class="alert-text"><strong>${sanitizeHTML(co)}</strong> — ${sanitizeHTML(cl)}</div><div class="alert-time">Vence: ${fmtDate(a.fecha_fin)} · <strong style="color:${d<=2?'#ff8a80':'var(--warning)'}">${d} día${d!==1?'s':''}</strong></div></div></div>`;}).join('')
                    :'<div style="text-align:center;padding:1.5rem;color:var(--text-muted)">Sin alertas activas.</div>';
            }catch(e){}
        }
        async function renderLastMovements(){
            try{
                const res=await ApiClient.request('GET','/movimientos?limit=5');
                const items=res?.data||[];
                document.getElementById('movCount').textContent=`${items.length} registros`;
                document.getElementById('movTable').innerHTML=items.map(m=>{
                    const co=DB_CONTENEDORES_API.find(c=>c.id_contenedor===m.id_contenedor)?.id_codigo||`#${m.id_contenedor}`;
                    return `<tr><td style="color:var(--text-muted)">#${m.id_movimiento}</td><td><strong>${sanitizeHTML(co)}</strong></td><td>${sanitizeHTML(m.ubicacion_origen||'—')}</td><td>${sanitizeHTML(m.ubicacion_destino||'—')}</td><td>${sanitizeHTML(m.medio_transporte||'—')}</td><td>${sanitizeHTML(m.responsable||'—')}</td><td style="font-size:.72rem;color:var(--text-muted)">${fmtDate(m.fecha_hora)}</td></tr>`;
                }).join('')||'<tr><td colspan="7"><div class="empty-state">Sin movimientos</div></td></tr>';
            }catch(e){}
        }

        /* ═══ CONTENEDORES ═══ */
        async function loadContainers(){
            showLoader('contLoader');
            try{
                const params=new URLSearchParams({skip:(currentPage-1)*rowsPerPage,limit:rowsPerPage});
                const cv=document.getElementById('filtCode')?.value; if(cv) params.set('codigo',cv);
                const sv=document.getElementById('filtState')?.value; if(sv) params.set('estado',sv);
                const clv=document.getElementById('filtClient')?.value; if(clv) params.set('id_cliente',clv);
                const tv=document.getElementById('filtType')?.value; if(tv) params.set('id_tipo',tv);
                const res=await ApiClient.request('GET',`/contenedores?${params}`);
                if(res?.ok){
                    DB_CONTENEDORES_API=res.data;
                    const norm=res.data.map(c=>({id:c.id_contenedor,codigo:c.id_codigo,tipo:DB_TIPOS.find(t=>t.id_tipo===c.id_tipo)?.nombre||`Tipo ${c.id_tipo}`,cliente:c.id_cliente?DB_CLIENTES.find(cl=>cl.id_cliente===c.id_cliente)?.nombre||`#${c.id_cliente}`:'Sin cliente',estado:c.estado,ubicacion:c.ubicacion_actual||'—',foto:c.ruta_imagen,fecha:fmtDate(c.created_at)}));
                    renderContainers(norm,res.meta);
                    populateModalSelects();
                }
            }catch(e){if(e.name!=='AbortError') showToast('Error cargando contenedores','error');}
            hideLoader('contLoader');
        }
        function renderContainers(data,meta){
            const tbody=document.getElementById('contTableBody');
            document.getElementById('contMetaInfo').textContent=`${meta.total} registros · Página ${meta.page||1} de ${meta.totalPages||1}`;
            if(!data.length){tbody.innerHTML=`<tr><td colspan="7"><div class="empty-state">Sin resultados</div></td></tr>`;return;}
            tbody.innerHTML=data.map(c=>`<tr>
                <td><strong>${sanitizeHTML(c.codigo)}</strong>${c.foto?` <i class="bi bi-image" style="color:var(--info);font-size:.75rem" title="${sanitizeHTML(c.foto)}"></i>`:''}</td>
                <td>${sanitizeHTML(c.tipo)}</td><td>${sanitizeHTML(c.cliente)}</td>
                <td>${getBadgeStatus(c.estado)}</td>
                <td style="font-size:.72rem;color:var(--text-muted)">${sanitizeHTML(c.ubicacion)}</td>
                <td style="font-size:.72rem;color:var(--text-muted)">${sanitizeHTML(c.fecha)}</td>
                <td><div class="table-actions">
                    ${canPerformAction('editContainer')?`<div class="btn-icon" onclick="openContainerModal(${c.id})" title="Editar"><i class="bi bi-pencil-fill"></i></div>`:''}
                    ${canPerformAction('deleteContainer')?`<div class="btn-icon danger" onclick="openConfirmModal(${c.id})" title="Eliminar"><i class="bi bi-trash-fill"></i></div>`:''}
                </div></td></tr>`).join('');
            renderPagination(meta);
        }
        function renderPagination(meta){
            const bar=document.getElementById('contPagination');
            let html=`<div class="rows-per-page">Filas: <select onchange="changeRows(this.value)"><option ${rowsPerPage==10?'selected':''}>10</option><option ${rowsPerPage==25?'selected':''}>25</option><option ${rowsPerPage==50?'selected':''}>50</option><option ${rowsPerPage==100?'selected':''}>100</option></select></div>`;
            if(meta.totalPages>1){
                html+=`<div class="pagination-controls"><button class="page-btn" onclick="changePage(${meta.page-1})" ${meta.page===1?'disabled':''}><i class="bi bi-chevron-left"></i></button>`;
                for(let i=Math.max(1,meta.page-2);i<=Math.min(meta.totalPages,meta.page+2);i++) html+=`<button class="page-btn ${i===meta.page?'active':''}" onclick="changePage(${i})">${i}</button>`;
                html+=`<button class="page-btn" onclick="changePage(${meta.page+1})" ${meta.page===meta.totalPages?'disabled':''}><i class="bi bi-chevron-right"></i></button></div>`;
            }
            bar.innerHTML=html;
        }
        function changePage(p){currentPage=p;loadContainers();}
        function changeRows(v){rowsPerPage=parseInt(v);currentPage=1;localStorage.setItem('rowsPref',rowsPerPage);loadContainers();}
        const debouncedFilterContainers=debounce(()=>{currentPage=1;loadContainers();},300);
        function filterContainers(){currentPage=1;loadContainers();}
        function resetFilters(){['filtCode','filtState','filtClient','filtType'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});currentPage=1;loadContainers();}
        const handleGlobalSearch=debounce(v=>{const el=document.getElementById('filtCode');if(el){el.value=v;currentPage=1;loadContainers();}},300);
        function toggleTransitFields(){
            const estado=document.getElementById('mState')?.value;
            const fields=document.getElementById('transitFields');
            if(fields) fields.style.display=estado==='en_transito'?'block':'none';
        }
        function openContainerModal(id=null){
            editId=id;
            document.getElementById('modalTitle').textContent=id?'Editar contenedor':'Nuevo contenedor';
            populateModalSelects();
            if(id){
                const c=DB_CONTENEDORES_API.find(x=>x.id_contenedor===id);
                if(c){document.getElementById('mCode').value=c.id_codigo;document.getElementById('mType').value=c.id_tipo;document.getElementById('mClient').value=c.id_cliente||'';document.getElementById('mState').value=c.estado;document.getElementById('mLocation').value=c.ubicacion_actual||'';document.getElementById('mPhoto').value=c.ruta_imagen||'';toggleTransitFields();}
            }else{
                ['mCode','mLocation','mPhoto','mOrigen','mDestino','mTransporte','mResponsable'].forEach(i=>{const el=document.getElementById(i);if(el)el.value='';});
                const ms=document.getElementById('mState');if(ms)ms.value='disponible';
                toggleTransitFields();
            }
            document.getElementById('modalContainer').classList.add('show');
        }
        function closeModal(id){
            const el=document.getElementById(id);if(el)el.classList.remove('show');
            if(id==='modalContainer')editId=null;
            if(id==='modalUser')editUserId=null;
            if(id==='modalClient')editClientId=null;
            if(id==='modalFact')editFactId=null;
            if(id==='modalRental')editRentalId=null;
        }
        async function saveContainer(){
            const code=document.getElementById('mCode').value.trim();
            if(!code){showToast('Código obligatorio','error');return;}
            const btn=document.getElementById('saveContainerBtn');
            btn.disabled=true; btn.innerHTML='<span style="font-size:.7rem">Guardando...</span>';
            try{
                const estado=document.getElementById('mState').value;
                const payload={id_codigo:code,id_tipo:parseInt(document.getElementById('mType').value),estado,ubicacion_actual:document.getElementById('mLocation').value.trim()||null,ruta_imagen:document.getElementById('mPhoto').value.trim()||null};
                const cv=document.getElementById('mClient').value; if(cv) payload.id_cliente=parseInt(cv);
                if(editId) await ApiClient.request('PUT',`/contenedores/${editId}`,payload);
                else {
                    const newCont=await ApiClient.request('POST','/contenedores',payload);
                    // Si en_transito, crear movimiento automaticamente
                    if(estado==='en_transito'&&document.getElementById('mOrigen').value.trim()&&newCont?.data){
                        const uid=getAuthUserId();
                        if(uid) await ApiClient.request('POST','/movimientos',{id_contenedor:newCont.data.id_contenedor,id_usuario:uid,ubicacion_origen:document.getElementById('mOrigen').value.trim(),ubicacion_destino:document.getElementById('mDestino').value.trim(),medio_transporte:document.getElementById('mTransporte').value.trim(),responsable:document.getElementById('mResponsable').value.trim()}).catch(()=>{});
                    }
                }
                closeModal('modalContainer');loadContainers();loadDashboardStats();showToast('Guardado correctamente');
            }catch(e){showToast(e.message||'Error al guardar','error');}
            btn.disabled=false; btn.innerHTML='<i class="bi bi-floppy-fill"></i> Guardar';
        }
        function openConfirmModal(id){
            const c=DB_CONTENEDORES_API.find(x=>x.id_contenedor===id)||{id_codigo:`#${id}`};
            document.getElementById('confirmMsg').textContent=`¿Eliminar ${c.id_codigo}? Esta acción no se puede deshacer.`;
            document.getElementById('confirmBtn').onclick=async()=>{
                try{await ApiClient.request('DELETE',`/contenedores/${id}`);closeModal('modalConfirm');loadContainers();loadDashboardStats();showToast('Eliminado','info');}
                catch(e){showToast(e.message||'Error','error');}
            };
            document.getElementById('modalConfirm').classList.add('show');
        }

        /* ═══ USUARIOS ═══ */
        function renderUsers(data){
            const tbody=document.getElementById('usersTable'); if(!tbody) return;
            const headers='<thead><tr><th>Usuario</th><th>Nombre</th><th>Email</th><th>Rol</th><th>Email verif.</th><th>Acciones</th></tr></thead>';
            document.getElementById('usersTable').parentElement.querySelector('thead').innerHTML=headers.replace(/<thead>|<\/thead>/g,'');
            tbody.innerHTML=data.map(u=>`<tr>
                <td>${sanitizeHTML(u.user)}</td>
                <td>${sanitizeHTML(u.nombres)}${u.apellidos?' '+sanitizeHTML(u.apellidos):''}</td>
                <td style="font-size:.75rem">${sanitizeHTML(u.email||'—')}</td>
                <td><span class="badge-status ${u.rol==='admin'?'disponible':u.rol==='supervisor'?'en_transito':u.rol==='auditor'?'asignado':'en_patio'}">${u.rol}</span></td>
                <td><span class="badge-status ${u.email_verificado?'disponible':'en_mantenimiento'}">${u.email_verificado?'Sí':'No'}</span></td>
                <td><div class="table-actions">
                    <div class="btn-icon" onclick="openUserModal(${u.id_usuario})" title="Editar"><i class="bi bi-pencil-fill"></i></div>
                    <div class="btn-icon danger" onclick="deleteUser(${u.id_usuario})" title="Eliminar"><i class="bi bi-trash-fill"></i></div>
                </div></td></tr>`).join('')||'<tr><td colspan="6"><div class="empty-state">Sin usuarios</div></td></tr>';
        }
        async function loadUsers(){
            if(currentUserRole!=='admin') return;
            const res=await ApiClient.request('GET','/usuarios').catch(()=>null);
            if(res?.ok){ DB_USUARIOS_API=res.data; renderUsers(res.data); }
        }
        function openUserModal(id=null){
            editUserId=id;
            document.getElementById('userModalTitle').textContent=id?'Editar usuario':'Nuevo usuario';
            if(id){
                const u=DB_USUARIOS_API.find(x=>x.id_usuario===id);
                if(u){document.getElementById('uName').value=u.nombres||'';document.getElementById('uApellidos').value=u.apellidos||'';document.getElementById('uEmail').value=u.email||'';document.getElementById('uUsername').value=u.user||'';document.getElementById('uPass').value='';document.getElementById('uRole').value=u.rol||'operador';}
            }else{
                ['uName','uApellidos','uEmail','uUsername','uPass'].forEach(i=>{const el=document.getElementById(i);if(el)el.value='';});
                const ur=document.getElementById('uRole');if(ur)ur.value='operador';
            }
            document.getElementById('modalUser').classList.add('show');
        }
        async function saveUser(){
            const name=document.getElementById('uName').value.trim(), user=document.getElementById('uUsername').value.trim();
            const pass=document.getElementById('uPass').value.trim(), role=document.getElementById('uRole').value;
            const apellidos=document.getElementById('uApellidos').value.trim(), email=document.getElementById('uEmail').value.trim();
            if(!name||!user){showToast('Nombre y usuario obligatorios','error');return;}
            if(!editUserId&&!pass){showToast('La contraseña es obligatoria','error');return;}
            const btn=document.getElementById('saveUserBtn'); btn.disabled=true;
            try{
                const payload=editUserId?{nombres:name,apellidos:apellidos||null,email:email||null,rol:role}:{nombres:name,apellidos:apellidos||null,email:email||null,user,password:pass,rol:role};
                if(pass&&editUserId) payload.password=pass;
                if(editUserId) await ApiClient.request('PUT',`/usuarios/${editUserId}`,payload);
                else await ApiClient.request('POST','/usuarios',payload);
                closeModal('modalUser');loadUsers();showToast('Usuario guardado');
            }catch(e){showToast(e.message||'Error guardando usuario','error');}
            btn.disabled=false;
        }
        async function deleteUser(id){
            const me=getAuthUserId();
            if(id===me){showToast('No puedes eliminar tu propia cuenta','error');return;}
            if(confirm('¿Eliminar usuario?')){
                try{await ApiClient.request('DELETE',`/usuarios/${id}`);loadUsers();showToast('Eliminado','info');}
                catch(e){showToast(e.message||'Error','error');}
            }
        }

        /* ═══ CLIENTES ═══ */
        async function loadClientesAPI(){
            const res=await ApiClient.request('GET','/clientes').catch(()=>null);
            if(res?.ok){ DB_CLIENTES=res.data; renderClientes(res.data); populateModalSelects(); populateFilters(); }
        }
        function filterClientesLocal(){
            const q=document.getElementById('filtClientSearch')?.value.toLowerCase();
            renderClientes(q?DB_CLIENTES.filter(c=>c.nombre.toLowerCase().includes(q)||c.nit.toLowerCase().includes(q)):DB_CLIENTES);
        }
        function renderClientes(data){
            const tbody=document.getElementById('clientsTable'); if(!tbody) return;
            document.getElementById('clientCount').textContent=`${data.length} clientes`;
            tbody.innerHTML=data.length?data.map(c=>`<tr>
                <td><strong>${sanitizeHTML(c.nombre)}</strong></td>
                <td style="font-size:.78rem;color:var(--text-muted)">${sanitizeHTML(c.nit)}</td>
                <td>${sanitizeHTML(c.telefono||'—')}</td>
                <td>${sanitizeHTML(c.email||'—')}</td>
                <td style="font-size:.78rem">${sanitizeHTML(c.direccion||'—')}</td>
                <td><div class="table-actions">
                    <div class="btn-icon" onclick="openClientModal(${c.id_cliente})" title="Editar"><i class="bi bi-pencil-fill"></i></div>
                    <div class="btn-icon danger" onclick="deleteCliente(${c.id_cliente})" title="Eliminar"><i class="bi bi-trash-fill"></i></div>
                </div></td></tr>`).join('')
                :'<tr><td colspan="6"><div class="empty-state">Sin clientes registrados</div></td></tr>';
        }
        function openClientModal(id=null){
            editClientId=id;
            document.getElementById('clientModalTitle').textContent=id?'Editar cliente':'Nuevo cliente';
            if(id){const c=DB_CLIENTES.find(x=>x.id_cliente===id);if(c){document.getElementById('cNombre').value=c.nombre||'';document.getElementById('cNit').value=c.nit||'';document.getElementById('cTelefono').value=c.telefono||'';document.getElementById('cEmail').value=c.email||'';document.getElementById('cDireccion').value=c.direccion||'';}}
            else{['cNombre','cNit','cTelefono','cEmail','cDireccion'].forEach(i=>{const el=document.getElementById(i);if(el)el.value='';});}
            document.getElementById('modalClient').classList.add('show');
        }
        async function saveCliente(){
            const nombre=document.getElementById('cNombre').value.trim(), nit=document.getElementById('cNit').value.trim();
            if(!nombre||!nit){showToast('Nombre y NIT obligatorios','error');return;}
            const btn=document.getElementById('saveClientBtn'); btn.disabled=true;
            try{
                const payload={nombre,nit,telefono:document.getElementById('cTelefono').value.trim()||null,email:document.getElementById('cEmail').value.trim()||null,direccion:document.getElementById('cDireccion').value.trim()||null};
                if(editClientId) await ApiClient.request('PUT',`/clientes/${editClientId}`,payload);
                else await ApiClient.request('POST','/clientes',payload);
                closeModal('modalClient');loadClientesAPI();showToast('Cliente guardado');
            }catch(e){showToast(e.message||'Error guardando cliente','error');}
            btn.disabled=false;
        }
        async function deleteCliente(id){
            if(confirm('¿Eliminar cliente?')){
                try{await ApiClient.request('DELETE',`/clientes/${id}`);loadClientesAPI();showToast('Eliminado','info');}
                catch(e){showToast(e.message||'Error','error');}
            }
        }

        /* ═══ FACTURACIÓN ═══ */
        async function loadFacturacionAPI(){
            const res=await ApiClient.request('GET','/facturacion').catch(()=>null);
            if(res?.ok){
                let data=res.data||[];
                const filtro=document.getElementById('filtFactEstado')?.value;
                if(filtro) data=data.filter(f=>f.estado_pago===filtro);
                DB_FACTURACION_API=data; renderFacturacion(data);
            }
        }
        function renderFacturacion(data){
            const tbody=document.getElementById('factTable'); if(!tbody) return;
            document.getElementById('factCount').textContent=`${data.length} facturas`;
            const today=new Date();
            tbody.innerHTML=data.length?data.map(f=>{
                const co=DB_CONTENEDORES_API.find(c=>c.id_contenedor===f.id_contenedor)?.id_codigo||`#${f.id_contenedor}`;
                let estado=f.estado_pago||'pendiente';
                if(estado==='pendiente'&&f.fecha_vencimiento&&new Date(f.fecha_vencimiento)<today) estado='mora';
                const ec=estado==='pagado'?'disponible':estado==='mora'?'fuera_de_servicio':'en_mantenimiento';
                return `<tr>
                    <td><strong>${sanitizeHTML(f.codigo_factura||`FAC-${f.id_factura}`)}</strong></td>
                    <td>${sanitizeHTML(co)}</td>
                    <td style="color:var(--success)">${fmtMoney(f.monto)}</td>
                    <td style="font-size:.72rem">${fmtDate(f.fecha_facturacion)}</td>
                    <td style="font-size:.72rem;color:${estado==='mora'?'#ff8a80':'var(--text-muted)'}">${fmtDate(f.fecha_vencimiento)}</td>
                    <td><span class="badge-status ${ec}">${estado}</span></td>
                    <td><div class="table-actions">
                        <div class="btn-icon" onclick="openFactModal(${f.id_factura})" title="Editar"><i class="bi bi-pencil-fill"></i></div>
                        <div class="btn-icon danger" onclick="deleteFact(${f.id_factura})" title="Eliminar"><i class="bi bi-trash-fill"></i></div>
                    </div></td></tr>`;
            }).join('')
            :'<tr><td colspan="7"><div class="empty-state">Sin facturas registradas</div></td></tr>';
        }
        function openFactModal(id=null){
            editFactId=id;
            document.getElementById('factModalTitle').textContent=id?'Editar factura':'Nueva factura';
            populateModalSelects();
            if(id){const f=DB_FACTURACION_API.find(x=>x.id_factura===id);if(f){document.getElementById('fContenedor').value=f.id_contenedor;document.getElementById('fMonto').value=f.monto;document.getElementById('fCodigo').value=f.codigo_factura||'';document.getElementById('fVencimiento').value=f.fecha_vencimiento||'';document.getElementById('fEstado').value=f.estado_pago||'pendiente';document.getElementById('fObs').value=f.observaciones||'';}}
            else{['fMonto','fCodigo','fVencimiento','fObs'].forEach(i=>{const el=document.getElementById(i);if(el)el.value='';});const fe=document.getElementById('fEstado');if(fe)fe.value='pendiente';}
            document.getElementById('modalFact').classList.add('show');
        }
        async function saveFactura(){
            const monto=parseFloat(document.getElementById('fMonto').value);
            if(!monto||monto<=0){showToast('Monto inválido','error');return;}
            const btn=document.getElementById('saveFactBtn'); btn.disabled=true;
            try{
                const payload={id_contenedor:parseInt(document.getElementById('fContenedor').value),monto,codigo_factura:document.getElementById('fCodigo').value.trim()||null,fecha_vencimiento:document.getElementById('fVencimiento').value||null,estado_pago:document.getElementById('fEstado').value,observaciones:document.getElementById('fObs').value.trim()||null};
                if(editFactId) await ApiClient.request('PUT',`/facturacion/${editFactId}`,payload);
                else await ApiClient.request('POST','/facturacion',payload);
                closeModal('modalFact');loadFacturacionAPI();showToast('Factura guardada');
            }catch(e){showToast(e.message||'Error guardando factura','error');}
            btn.disabled=false;
        }
        async function deleteFact(id){
            if(confirm('¿Eliminar factura?')){
                try{await ApiClient.request('DELETE',`/facturacion/${id}`);loadFacturacionAPI();showToast('Eliminada','info');}
                catch(e){showToast(e.message||'Error','error');}
            }
        }

        /* ═══ ARRENDAMIENTOS ═══ */
        async function loadArrendamientosAPI(){
            const estado=document.getElementById('arrFilterState')?.value;
            const params=new URLSearchParams(); if(estado) params.set('estado',estado);
            const res=await ApiClient.request('GET',`/arrendamientos?${params}`).catch(()=>null);
            if(res?.ok){ DB_ARRENDAMIENTOS_API=res.data||[]; renderRentals(DB_ARRENDAMIENTOS_API); }
        }
        function renderRentals(data){
            const tbody=document.getElementById('arrTable'); if(!tbody) return;
            document.getElementById('arrCount').textContent=`${data.length} contratos`;
            const today=new Date();
            tbody.innerHTML=data.length?data.map(a=>{
                const co=DB_CONTENEDORES_API.find(c=>c.id_contenedor===a.id_contenedor)?.id_codigo||`#${a.id_contenedor}`;
                const cl=DB_CLIENTES.find(c=>c.id_cliente===a.id_cliente)?.nombre||`#${a.id_cliente}`;
                const activo=a.estado_arrendamiento==='activo';
                const dias=a.fecha_fin?Math.ceil((new Date(a.fecha_fin)-today)/86400000):null;
                const enAlerta=dias!==null&&dias<=7&&activo;
                return `<tr>
                    <td><strong>${sanitizeHTML(co)}</strong></td>
                    <td>${sanitizeHTML(cl)}</td>
                    <td style="font-size:.78rem">${fmtDate(a.fecha_inicio)}</td>
                    <td style="font-size:.78rem;color:${enAlerta?'#ff8a80':'var(--text-muted)'}">${fmtDate(a.fecha_fin)}${enAlerta?` <span style="font-size:.65rem;color:#ff8a80">(${dias}d)</span>`:''}</td>
                    <td style="color:var(--success)">${fmtMoney(a.valor_alquiler)}</td>
                    <td><span class="badge-status ${activo?'disponible':'fuera_de_servicio'}">${activo?'Activo':'Finalizado'}</span></td>
                    <td><div class="table-actions">
                        <div class="btn-icon" onclick="openRentalModal(${a.id_arrendamiento})" title="Editar"><i class="bi bi-pencil-fill"></i></div>
                        <div class="btn-icon danger" onclick="deleteRental(${a.id_arrendamiento})" title="Eliminar"><i class="bi bi-trash-fill"></i></div>
                    </div></td></tr>`;
            }).join('')
            :'<tr><td colspan="7"><div class="empty-state">Sin contratos registrados</div></td></tr>';
        }
        function openRentalModal(id=null){
            editRentalId=id;
            document.getElementById('rentalModalTitle').textContent=id?'Editar contrato':'Nuevo contrato de arrendamiento';
            populateModalSelects();
            if(id){const a=DB_ARRENDAMIENTOS_API.find(x=>x.id_arrendamiento===id);if(a){document.getElementById('rContenedor').value=a.id_contenedor;document.getElementById('rCliente').value=a.id_cliente;document.getElementById('rInicio').value=a.fecha_inicio;document.getElementById('rFin').value=a.fecha_fin||'';document.getElementById('rValor').value=a.valor_alquiler;document.getElementById('rEstado').value=a.estado_arrendamiento;}}
            else{['rInicio','rFin','rValor'].forEach(i=>{const el=document.getElementById(i);if(el)el.value='';});const re=document.getElementById('rEstado');if(re)re.value='activo';}
            document.getElementById('modalRental').classList.add('show');
        }
        async function saveRental(){
            const valor=parseFloat(document.getElementById('rValor').value);
            const inicio=document.getElementById('rInicio').value;
            if(!inicio||!valor){showToast('Fecha inicio y valor son obligatorios','error');return;}
            const btn=document.getElementById('saveRentalBtn'); btn.disabled=true;
            try{
                const payload={id_contenedor:parseInt(document.getElementById('rContenedor').value),id_cliente:parseInt(document.getElementById('rCliente').value),fecha_inicio:inicio,fecha_fin:document.getElementById('rFin').value||null,valor_alquiler:valor,estado_arrendamiento:document.getElementById('rEstado').value};
                if(editRentalId) await ApiClient.request('PUT',`/arrendamientos/${editRentalId}`,payload);
                else await ApiClient.request('POST','/arrendamientos',payload);
                closeModal('modalRental');loadArrendamientosAPI();loadDashboardStats();showToast('Contrato guardado');
            }catch(e){showToast(e.message||'Error guardando contrato','error');}
            btn.disabled=false;
        }
        async function deleteRental(id){
            if(confirm('¿Eliminar contrato?')){
                try{await ApiClient.request('DELETE',`/arrendamientos/${id}`);loadArrendamientosAPI();showToast('Eliminado','info');}
                catch(e){showToast(e.message||'Error','error');}
            }
        }

        /* ═══ MOVIMIENTOS ═══ */
        async function loadMovimientosAPI(){
            const params=new URLSearchParams();
            const c=document.getElementById('movFilterContainer')?.value; if(c) params.set('id_contenedor',c);
            const s=document.getElementById('movFilterStart')?.value; if(s) params.set('fecha_inicio',s);
            const e=document.getElementById('movFilterEnd')?.value; if(e) params.set('fecha_fin',e);
            const res=await ApiClient.request('GET',`/movimientos?${params}&limit=200`).catch(()=>null);
            if(res?.ok){
                const data=res.data||[];
                document.getElementById('movPageCount').textContent=`${data.length} registros`;
                document.getElementById('movPageTable').innerHTML=data.map(m=>{
                    const co=DB_CONTENEDORES_API.find(c=>c.id_contenedor===m.id_contenedor)?.id_codigo||`#${m.id_contenedor}`;
                    return `<tr><td style="color:var(--text-muted)">#${m.id_movimiento}</td><td><strong>${sanitizeHTML(co)}</strong></td><td>${sanitizeHTML(m.ubicacion_origen||'—')}</td><td>${sanitizeHTML(m.ubicacion_destino||'—')}</td><td>${sanitizeHTML(m.medio_transporte||'—')}</td><td>${sanitizeHTML(m.responsable||'—')}</td><td style="font-size:.72rem;color:var(--text-muted)">${fmtDate(m.fecha_hora)}</td></tr>`;
                }).join('')||'<tr><td colspan="7"><div class="empty-state">Sin movimientos</div></td></tr>';
            }
        }
        function populateMovFilter(){
            const s=document.getElementById('movFilterContainer'); if(!s) return;
            s.innerHTML='<option value="">Todos los contenedores</option>'+DB_CONTENEDORES_API.map(c=>`<option value="${c.id_contenedor}">${sanitizeHTML(c.id_codigo)}</option>`).join('');
        }
        function resetMovementFilters(){['movFilterContainer','movFilterStart','movFilterEnd'].forEach(id=>{const el=document.getElementById(id);if(el)el.value='';});loadMovimientosAPI();}

        /* ═══ HISTORIAL ═══ */
        function populateHistFilter(){
            const s=document.getElementById('histFilterContainer'); if(!s) return;
            s.innerHTML='<option value="">Seleccionar contenedor</option>'+DB_CONTENEDORES_API.map(c=>`<option value="${c.id_contenedor}">${sanitizeHTML(c.id_codigo)}</option>`).join('');
        }
        async function showHistory(){
            const id=document.getElementById('histFilterContainer').value;
            document.getElementById('historyEmpty').style.display=id?'none':'block';
            document.getElementById('historyContent').style.display=id?'block':'none';
            if(!id) return;
            try{
                const res=await ApiClient.request('GET',`/contenedores/${id}/historial`);
                if(!res?.ok) return;
                const data=res.data, movs=data.movimientos||[], hist=data.historial_estado||[], arr=data.arrendamientos||[];
                document.getElementById('historyContent').innerHTML=`
                    <h5 style="color:var(--text-primary);margin-bottom:.8rem"><i class="bi bi-arrow-left-right" style="color:var(--info)"></i> Movimientos</h5>
                    ${movs.length?`<div style="overflow-x:auto"><table class="data-table"><thead><tr><th>ID</th><th>Origen</th><th>Destino</th><th>Transporte</th><th>Responsable</th><th>Fecha</th></tr></thead><tbody>${movs.map(m=>`<tr><td>#${m.id_movimiento}</td><td>${sanitizeHTML(m.ubicacion_origen||'—')}</td><td>${sanitizeHTML(m.ubicacion_destino||'—')}</td><td>${sanitizeHTML(m.medio_transporte||'—')}</td><td>${sanitizeHTML(m.responsable||'—')}</td><td style="font-size:.72rem">${fmtDate(m.fecha_hora)}</td></tr>`).join('')}</tbody></table></div>`:'<p style="color:var(--text-muted);margin:.5rem 0 1rem">Sin movimientos registrados.</p>'}
                    <h5 style="color:var(--text-primary);margin:1.2rem 0 .8rem"><i class="bi bi-arrow-repeat" style="color:var(--warning)"></i> Cambios de estado</h5>
                    ${hist.length?`<div style="overflow-x:auto"><table class="data-table"><thead><tr><th>Inicio</th><th>Fin</th><th>Estado</th></tr></thead><tbody>${hist.map(h=>`<tr><td style="font-size:.78rem">${fmtDate(h.fecha_inicio)}</td><td style="font-size:.78rem">${fmtDate(h.fecha_fin)}</td><td>${getBadgeStatus(h.estado)}</td></tr>`).join('')}</tbody></table></div>`:'<p style="color:var(--text-muted);margin:.5rem 0 1rem">Sin cambios de estado.</p>'}
                    <h5 style="color:var(--text-primary);margin:1.2rem 0 .8rem"><i class="bi bi-calendar2-week" style="color:var(--success)"></i> Arrendamientos</h5>
                    ${arr.length?`<div style="overflow-x:auto"><table class="data-table"><thead><tr><th>Cliente</th><th>Inicio</th><th>Fin</th><th>Valor</th><th>Estado</th></tr></thead><tbody>${arr.map(a=>{const cl=DB_CLIENTES.find(c=>c.id_cliente===a.id_cliente)?.nombre||`#${a.id_cliente}`;return`<tr><td>${sanitizeHTML(cl)}</td><td style="font-size:.78rem">${fmtDate(a.fecha_inicio)}</td><td style="font-size:.78rem">${fmtDate(a.fecha_fin)}</td><td>${fmtMoney(a.valor_alquiler)}</td><td><span class="badge-status ${a.estado_arrendamiento==='activo'?'disponible':'fuera_de_servicio'}">${a.estado_arrendamiento}</span></td></tr>`;}).join('')}</tbody></table></div>`:'<p style="color:var(--text-muted);margin:.5rem 0 1rem">Sin arrendamientos.</p>'}
                `;
            }catch(e){showToast('Error cargando historial','error');}
        }

        /* ═══ ZONAS ═══ */
        function getZone(loc){if(!loc)return'Sin zona';const l=loc.toLowerCase();if(l.includes('cartagena'))return'Puerto Cartagena';if(l.includes('barranquilla'))return'Barranquilla';if(l.includes('bogot'))return'Bogotá';if(l.includes('medell'))return'Medellín';if(l.includes('cali'))return'Cali';if(l.includes('bucaramanga'))return'Bucaramanga';if(l.includes('taller')||l.includes('mantenimiento'))return'Taller/Mantenimiento';return'Otros';}
        async function renderZoneData(){
            const res=await ApiClient.request('GET','/dashboard/zonas/distribucion').catch(()=>null);
            if(!res?.ok) return;
            const zones=res.data, entries=Object.entries(zones);
            const filtZone=document.getElementById('filtZone')?.value;
            let filtered=filtZone?entries.filter(([z])=>z.toLowerCase().includes(filtZone.toLowerCase())):entries;
            document.getElementById('zoneCount').textContent=`${filtered.length} zonas`;
            const tbody=document.getElementById('zoneTable');
            if(!filtered.length){tbody.innerHTML='<tr><td colspan="6"><div class="empty-state">Sin datos de zonas</div></td></tr>';return;}
            let totals={total:0,disponible:0,en_transito:0,en_patio:0,otros:0}, html='';
            filtered.forEach(([z,d])=>{Object.keys(totals).forEach(k=>totals[k]+=(d[k]||0));html+=`<tr style="cursor:pointer" onclick="document.getElementById('filtZone').value='${z.split('/')[0].trim()}';renderZoneData()"><td><strong>${sanitizeHTML(z)}</strong></td><td>${d.total}</td><td style="color:var(--success)">${d.disponible}</td><td style="color:var(--warning)">${d.en_transito}</td><td style="color:#ce93d8">${d.en_patio}</td><td>${d.otros}</td></tr>`;});
            html+=`<tr style="border-top:2px solid var(--border-color);font-weight:700"><td>Total</td><td>${totals.total}</td><td style="color:var(--success)">${totals.disponible}</td><td style="color:var(--warning)">${totals.en_transito}</td><td style="color:#ce93d8">${totals.en_patio}</td><td>${totals.otros}</td></tr>`;
            tbody.innerHTML=html;
            const top=filtered.length?filtered.sort((a,b)=>b[1].total-a[1].total)[0]:null;
            const sinUb=DB_CONTENEDORES_API.filter(c=>!c.ubicacion_actual).length;
            const alertas=DB_ARRENDAMIENTOS_API.filter(a=>{const d=Math.ceil((new Date(a.fecha_fin||'2099-01-01')-new Date())/86400000);return d<=7&&d>=0&&a.estado_arrendamiento==='activo';}).length;
            document.getElementById('zonesCards').innerHTML=`<div class="zone-card"><div class="num">${top?sanitizeHTML(top[0]):'—'}</div><div class="lbl">Zona principal</div></div><div class="zone-card"><div class="num" style="color:var(--warning)">${alertas}</div><div class="lbl">Alertas</div></div><div class="zone-card"><div class="num" style="color:var(--text-muted)">${sinUb}</div><div class="lbl">Sin ubicación</div></div>`;
            initMap(entries);
        }
        function filterZones(){renderZoneData();}
        function resetZones(){const fz=document.getElementById('filtZone'),fs=document.getElementById('filtZoneState');if(fz)fz.value='';if(fs)fs.value='';renderZoneData();}
        function initMap(entries=[]){
            const c=document.getElementById('leafletMap'); if(!c) return;
            if(!mapInit){mapInstance=L.map(c).setView([4.6,-74.2],5.8);L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{attribution:'© OpenStreetMap'}).addTo(mapInstance);mapInit=true;}
            else{mapInstance.eachLayer(l=>{if(l instanceof L.CircleMarker)mapInstance.removeLayer(l);});}
            const coords={'Puerto Cartagena':{lat:10.4,lon:-75.5},'Barranquilla':{lat:10.98,lon:-74.78},'Bogotá':{lat:4.61,lon:-74.08},'Medellín':{lat:6.25,lon:-75.56},'Cali':{lat:3.44,lon:-76.52},'Bucaramanga':{lat:7.12,lon:-73.12},'Taller/Mantenimiento':{lat:4.8,lon:-74.2}};
            entries.forEach(([zona,data])=>{const coord=coords[zona];if(!coord)return;const cnt=data.total,r=Math.max(cnt*2.5,8),col=cnt>=6?'#D32F2F':cnt>=3?'#ffca28':'#42a5f5';L.circleMarker([coord.lat,coord.lon],{radius:r,color:col,fillColor:col,fillOpacity:0.7,weight:1.5}).addTo(mapInstance).bindPopup(`<strong>${zona}</strong><br>${cnt} contenedor${cnt!==1?'es':''}<br>Disp: ${data.disponible} | Tráns: ${data.en_transito}`);});
        }

        /* ═══ EXPORT CSV ═══ */
        function exportCSV(type){
            let csv='';
            if(type==='contenedores'){
                csv='Código,Tipo,Cliente,Estado,Ubicación,Foto,Fecha\\n';
                DB_CONTENEDORES_API.forEach(c=>{const ti=DB_TIPOS.find(t=>t.id_tipo===c.id_tipo)?.nombre||c.id_tipo;const cl=DB_CLIENTES.find(cl=>cl.id_cliente===c.id_cliente)?.nombre||'Sin cliente';csv+=`${c.id_codigo},${ti},${cl},${c.estado},${c.ubicacion_actual||''},${c.ruta_imagen||''},${c.created_at||''}\\n`;});
            }else if(type==='facturacion'){
                csv='Código,Contenedor,Monto,Emisión,Vencimiento,Estado\\n';
                DB_FACTURACION_API.forEach(f=>{const co=DB_CONTENEDORES_API.find(c=>c.id_contenedor===f.id_contenedor)?.id_codigo||f.id_contenedor;csv+=`${f.codigo_factura||f.id_factura},${co},${f.monto},${f.fecha_facturacion||''},${f.fecha_vencimiento||''},${f.estado_pago}\\n`;});
            }
            if(!csv){showToast('Sin datos para exportar','error');return;}
            const b=new Blob([csv],{type:'text/csv'}),u=URL.createObjectURL(b),a=document.createElement('a');
            a.href=u;a.download=`${type}_${new Date().toISOString().slice(0,10)}.csv`;a.click();URL.revokeObjectURL(u);showToast('CSV descargado');
        }

        /* ═══ NAVEGACIÓN ═══ */
        const PAGE_TITLES={panel:'Panel de Operaciones',contenedores:'Contenedores',zonas:'Por Zona',movimientos:'Movimientos',arrendamientos:'Arrendamientos',historial:'Historial',clientes:'Clientes',facturacion:'Facturación',reportes:'Reportes',usuarios:'Usuarios'};
        function navigateTo(pageId,el){
            if(!canAccessPage(pageId)){showToast('Sin permisos','error');return;}
            document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
            document.getElementById('page-'+pageId)?.classList.add('active');
            if(el) el.classList.add('active');
            document.getElementById('pageTitle').textContent=PAGE_TITLES[pageId]||pageId;
            document.getElementById('breadcrumb').textContent=`Inicio › ${PAGE_TITLES[pageId]||pageId}`;
            if(window.innerWidth<=768) closeMobileSidebar();
            if(pageId==='panel'){loadDashboardStats();renderAlerts();renderLastMovements();applyTheme();}
            else if(pageId==='contenedores'){if(DB_TIPOS.length){loadContainers();populateFilters();}else{loadReferenceData().then(()=>loadContainers());}}
            else if(pageId==='zonas'){if(!DB_CONTENEDORES_API.length)loadContainers().then(()=>renderZoneData());else renderZoneData();}
            else if(pageId==='movimientos'){populateMovFilter();loadMovimientosAPI();}
            else if(pageId==='arrendamientos'){if(!DB_CONTENEDORES_API.length){loadReferenceData().then(()=>{loadContainers().then(()=>loadArrendamientosAPI());});}else loadArrendamientosAPI();}
            else if(pageId==='historial') populateHistFilter();
            else if(pageId==='clientes') loadClientesAPI();
            else if(pageId==='facturacion'){if(!DB_CONTENEDORES_API.length)loadContainers().then(()=>loadFacturacionAPI());else loadFacturacionAPI();}
            else if(pageId==='reportes'){loadDashboardStats();}
            else if(pageId==='usuarios') loadUsers();
        }

        /* ═══ SIDEBAR & THEME ═══ */
        function closeMobileSidebar(){document.getElementById('sidebar').classList.remove('open');document.getElementById('sidebarOverlay').classList.remove('show');}
        function toggleSidebar(){
            if(window.innerWidth<=768){document.getElementById('sidebar').classList.toggle('open');document.getElementById('sidebarOverlay').classList.toggle('show');}
            else{document.getElementById('sidebar').classList.toggle('collapsed');localStorage.setItem('sidebar_col',document.getElementById('sidebar').classList.contains('collapsed')?'1':'0');}
            const ic=document.getElementById('sidebarToggle')?.querySelector('i');
            if(ic) ic.className=document.getElementById('sidebar').classList.contains('collapsed')?'bi bi-chevron-right':'bi bi-chevron-left';
        }
        function setTheme(t){
            document.documentElement.setAttribute('data-bs-theme',t);
            const ic=document.getElementById('themeToggle')?.querySelector('i');
            if(ic) ic.className=t==='light'?'bi bi-moon-fill':'bi bi-sun-fill';
            localStorage.setItem('theme',t); applyTheme();
        }
        function logout(){TokenManager.clear();window.location.href='/login';}

        /* ═══ INIT ═══ */
        document.addEventListener('DOMContentLoaded', async () => {
            const token=getAuthToken();
            if(!token){window.location.href='/login';return;}
            const role=getAuthRole(), username=getAuthUser();
            if(!role){window.location.href='/login';return;}
            currentUserRole=role;
            document.getElementById('sidebarUser').textContent=username||'Usuario';
            document.getElementById('sidebarRole').textContent='Rol: '+role;
            document.getElementById('userAvatar').textContent=(username||'AD').substring(0,2).toUpperCase();
            rowsPerPage=parseInt(localStorage.getItem('rowsPref'))||10;
            applyRoleBasedUI();
            const savedTheme=localStorage.getItem('theme')||'dark';
            setTheme(savedTheme);
            document.getElementById('themeToggle').addEventListener('click',()=>setTheme(document.documentElement.getAttribute('data-bs-theme')==='dark'?'light':'dark'));
            document.getElementById('sidebarToggle').addEventListener('click',toggleSidebar);
            if(localStorage.getItem('sidebar_col')==='1') document.getElementById('sidebar').classList.add('collapsed');
            ['modalContainer','modalConfirm','modalUser','modalClient','modalFact','modalRental'].forEach(id=>{const el=document.getElementById(id);if(el)el.addEventListener('click',function(e){if(e.target===this)closeModal(id);});});
            document.addEventListener('keydown',e=>{
                if(e.key==='Escape'){['modalContainer','modalConfirm','modalUser','modalClient','modalFact','modalRental'].forEach(id=>closeModal(id));closeNotifPanel();closeProfilePanel();}
                if((e.ctrlKey||e.metaKey)&&e.key==='k'){e.preventDefault();document.getElementById('globalSearch')?.focus();}
            });
            await loadReferenceData();
            await Promise.all([loadDashboardStats(),loadNotifications()]);
            renderAlerts();renderLastMovements();loadContainers();
            if(currentUserRole==='admin') loadUsers();
            setInterval(loadNotifications,180000);
            setInterval(()=>{loadDashboardStats();renderAlerts();renderLastMovements();},300000);
            setInterval(()=>{const m=Math.floor((Date.now()-performance.timeOrigin)/60000);const el=document.getElementById('updateLabel');const el2=document.getElementById('lastUpdate');if(el)el.textContent=`Última actualización: hace ${m} min`;if(el2)el2.textContent=`Actualizado hace ${m} min`;},60000);
        });
    </script>
</body>
</html>"""

new_content = html_part + new_js
with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done. Total length:', len(new_content))
