# --- INITIALIZE SESSION STATE ---
# --- VERIFICAR SESSÃO EXISTENTE ---
if not st.session_state.logado:
    token_do_cookie = cookie_manager.get("seindec_token")
    if token_do_cookie:
        # ✅ Tenta recuperar usuário do cookie
        usuario_recuperado = verificar_sessao()
        if usuario_recuperado:
            st.session_state.logado = True
            st.session_state.usuario = usuario_recuperado
            st.rerun()
        # Senão, mostra login
    
    # Se não tem cookie ou sessão expirou, mostra formulário
    st.set_page_config(layout="centered")
    col1, col2, col3 = st.columns([2, 4, 2])
    with col2:
        st.image("assets/logo_login1.png", use_container_width=True)
    
    # ✨ NOVO: Adicionar abas agora com 3 opções: Login, Cadastro e Recuperação
    tab_login, tab_cadastro, tab_recuperacao = st.tabs([
        "🔐 Login", 
        "📝 Cadastrar Usuário",
        "🔑 Esqueci a Senha"
    ])
        
    with tab_login:
        with st.form("form_login"):
            u_log = st.text_input("Usuário")
            s_log = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar"):
                df_u = ler_aba("usuarios")
                if df_u.empty:
                    st.error("Usuário ou senha incorretos.")
                else:    
                    # FIX: Usar coluna correta (senha_hash) e verificar com hash
                    col_login = "login"
                    col_senha = "senha_hash"
                    
                    user_row = df_u[df_u[col_login] == u_log]
                    if not user_row.empty:
                        hash_armazenado = str(user_row.iloc[0][col_senha])
                        if verificar_senha(s_log, hash_armazenado):
                            criar_sessao(u_log)
                            st.success("Login realizado!")
                            st.rerun()
                        else:
                            st.error("Usuário ou senha incorretos.")
                    else:
                        st.error("Usuário ou senha incorretos.")
    
    with tab_cadastro:
        with st.form("form_registro"):
            st.info("Crie uma conta para acessar o sistema.")
            n_reg = st.text_input("Nome Completo")
            u_reg = st.text_input("Novo Usuário (sem espaços)")
            s_reg = st.text_input("Nova Senha", type="password")
            s_conf = st.text_input("Confirme a Senha", type="password")
            c_reg = st.text_input("Código de Administrador", type="password")
            if st.form_submit_button("Cadastrar"):
                df_u = ler_aba("usuarios")
                if not n_reg or not u_reg or not s_reg or not c_reg:
                    st.warning("Preencha todos os campos.")
                elif n_reg in df_u["nome_completo"].values:
                    st.error("Este nome já está cadastrado.")
                elif u_reg in df_u["login"].values:
                    st.error("Este usuário já existe.")
                elif s_reg != s_conf:
                    st.error("As senhas não coincidem.")
                elif c_reg != "procon@723_arap0":
                    st.error("Código incorreto.")
                else:
                    novo_id = gerar_id_unico()
                    # FIX: Usar hash_senha ao registrar
                    novo_u = pd.DataFrame([{
                        "id": novo_id, 
                        "nome_completo": n_reg,
                        "login": u_reg, 
                        "senha_hash": hash_senha(s_reg)
                    }])
                    salvar_dados("usuarios", pd.concat([df_u, novo_u], ignore_index=True))
                    st.success("Usuário cadastrado com sucesso! Agora faça login.")
    
    # ✨ NOVO: Aba para recuperação de senha
    with tab_recuperacao:
        with st.form("form_recuperacao"):
            st.info("Redefina sua senha preenchendo os campos abaixo.")
            
            u_recup = st.text_input("Usuário Existente")
            s_nova = st.text_input("Senha Nova", type="password")
            s_conf_recup = st.text_input("Confirme Senha Nova", type="password")
            c_recup = st.text_input("Código de Administrador", type="password")
            
            if st.form_submit_button("Atualizar Senha"):
                # Validação 1: Verificar se todos os campos estão preenchidos
                if not u_recup or not s_nova or not s_conf_recup or not c_recup:
                    st.error("❌ Preencha todos os campos.")
                
                # Validação 2: Verificar se as senhas correspondem
                elif s_nova != s_conf_recup:
                    st.error("❌ As senhas não coincidem.")
                
                # Validação 3: Verificar o código de administrador
                elif c_recup != "procon@723_arap0":
                    st.error("❌ Código de administrador incorreto.")
                
                else:
                    # Lê dados dos usuários
                    df_u = ler_aba("usuarios")
                    
                    # Validação 4: Verificar se o usuário existe
                    user_row = df_u[df_u["login"] == u_recup]
                    if user_row.empty:
                        st.error("❌ Usuário não encontrado.")
                    
                    else:
                        # ✅ Todas as validações passaram - atualizar senha
                        try:
                            # Atualizar a senha com hash
                            df_u.loc[df_u["login"] == u_recup, "senha_hash"] = hash_senha(s_nova)
                            
                            # Salvar os dados atualizados
                            salvar_dados("usuarios", df_u)
                            
                            st.success("✅ Senha atualizada com sucesso!")
                            st.info("Você será redirecionado para o login em 2 segundos...")
                            
                            # Aguardar e recarregar a página
                            import time
                            time.sleep(2)
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao atualizar a senha: {str(e)}")
    
    st.stop()
