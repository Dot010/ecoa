# ecoa

Rede social no estilo microblog, feita com **Django** e **Django REST Framework**. Projeto final do curso Desenvolvedor Full Stack Python (EBAC).

**🔗 Online:** https://ecoa-xch6.onrender.com

> O plano gratuito do Render "dorme" quando o site fica sem uso. O primeiro acesso pode levar até 1 minuto.

## Funcionalidades

- Cadastro, login e logout
- Editar perfil: foto, nome, bio e troca de senha (todos os campos são opcionais)
- Seguir e deixar de seguir usuários, com listas de seguidores e de quem você segue
- Feed apenas com posts de quem você segue, paginado
- Publicar, curtir, comentar e apagar o próprio post
- Sugestões de quem seguir
- Layout responsivo (desktop e celular)
- API REST completa, autenticada por token

## Tecnologias

| Camada | Ferramentas |
|---|---|
| Back-end | Python 3.15, Django 6, Django REST Framework |
| Front-end | Templates do Django + CSS próprio |
| Banco de dados | PostgreSQL (Neon) em produção, SQLite no desenvolvimento |
| Deploy | Docker, Render (Blueprint), Gunicorn, WhiteNoise |
| Qualidade | 37 testes automatizados, Black |

## Como rodar localmente

Pré-requisitos: Python 3.15 e [Poetry](https://python-poetry.org/).

```bash
git clone https://github.com/Dot010/ecoa.git
cd ecoa
poetry install
```

Crie o arquivo `.env` a partir do exemplo e troque a `SECRET_KEY` por um valor seu:

```bash
cp .env.example .env
```

Crie as tabelas e suba o servidor:

```bash
poetry run python manage.py migrate
poetry run python manage.py runserver
```

Acesse http://127.0.0.1:8000/

## Testes

```bash
poetry run python manage.py test
```

## API

Base: `/api/`. Para rotas protegidas, envie o cabeçalho `Authorization: Token <seu-token>`.

| Método | Rota | O que faz |
|---|---|---|
| POST | `/api/auth/register/` | Cria a conta e devolve o token |
| POST | `/api/auth/login/` | Login (username e senha) e devolve o token |
| GET / PATCH | `/api/me/` | Ver ou editar o próprio perfil |
| POST | `/api/me/password/` | Trocar a senha |
| GET | `/api/users/<username>/` | Perfil de um usuário |
| POST / DELETE | `/api/users/<username>/follow/` | Seguir / deixar de seguir |
| GET | `/api/users/<username>/followers/` | Seguidores |
| GET | `/api/users/<username>/following/` | Quem o usuário segue |
| GET | `/api/users/<username>/posts/` | Posts do usuário |
| GET / POST | `/api/posts/` | Listar / publicar posts |
| GET / PATCH / DELETE | `/api/posts/<id>/` | Ver, editar ou apagar (só o autor edita ou apaga) |
| POST / DELETE | `/api/posts/<id>/like/` | Curtir / descurtir |
| GET / POST | `/api/posts/<id>/comments/` | Ver / adicionar comentários |
| GET | `/api/feed/` | Feed com posts de quem você segue |

## Deploy

O deploy é feito no **Render** com o `render.yaml` (Blueprint) e o `Dockerfile`. A cada push na `main`, o Render:

1. monta a imagem Docker;
2. roda o `start.sh`: `migrate`, `collectstatic` e `gunicorn`.

A `SECRET_KEY` é gerada pelo próprio Render. Os dados do banco (`SQL_HOST`, `SQL_DATABASE`, `SQL_USER`, `SQL_PASSWORD`) ficam no painel do Render, **nunca no repositório**.

**Limitação conhecida:** no plano gratuito, o disco do servidor é temporário, então as fotos de perfil podem sumir quando o serviço reinicia. Próximo passo: guardar as imagens em um serviço externo (ex.: Cloudinary).

## Próximos passos

- Front-end em Next.js consumindo a API
- Armazenamento externo para as fotos
- Busca, notificações e hashtags

---

Feito por **Jonathan Carvalho** · [GitHub](https://github.com/Dot010)
