from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from typing import Annotated, Generic, Optional, TypeVar
from pydantic import BaseModel
from sqlmodel import  SQLModel, Session, create_engine, select,Field

# from pydantic import BaseModel

#custom type 
class Campaign(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    #note: default_factory-> takes a function to use for generating a value each time an object is created,
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)


class CampaignCreate(SQLModel):
    name:str
    due_date:datetime | None=None
    


sqlite_file_name="database.db"
sqlite_url=f"sqlite:///{sqlite_file_name}"

# allows FastAPI to use the same db across multiple threads
connect_args={"check_same_thread":False}
#engine maintains the conenction to db 
engine =create_engine(sqlite_url,connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# def create_sessions():
#     with Session(engine) as session:
#         yield session
#sessio nwill use engine to do work with the db 
def get_session():
    with Session(engine) as session:
        yield session
        
SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
#helps us to run the db function on startup 
async def lifespan(app:FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        #if it didint return any rows , then it will instert two rows 
        if not session.exec(select(Campaign)).first():
            session.add_all([
                #preloaded in db 
                Campaign(name="Summer Launch", due_date=datetime.now()),
                Campaign(name="Black Friday", due_date=datetime.now()),
            ])
            session.commit()

    yield
#note: anything before the yield will run on the startup and anything after the yield will run after 

app = FastAPI(root_path="/api/v1",lifespan=lifespan)
#associate a web page visit to a certain function (path opoeration function ) or u can call it decorator 
@app.get("/")
async def root():
    return {"message":"Hey"}

#custom type ot handle the structure of the response(specific to an endpoint, its better to create a generic one )
# class CampaignsResponse(BaseModel):
#     campaigns:list[Campaign]

T=TypeVar("T")
#generic custom type
class Response(BaseModel,Generic[T]):
    data:T
    
class PaginatedResponse(BaseModel, Generic[T]):
      data: T
      next: Optional[str]
      prev: Optional[str]    

@app.get("/campaigns",response_model=PaginatedResponse[list[Campaign]])
async def read_campaigns(request:Request,session:SessionDep,page:int=Query(1,ge=1),page_size:int =Query(20,ge=1)): # type: ignore
    #we used exec bc we're dealing with multipe values 
    limit=page_size
    offset=(page-1)*limit
    data= session.exec(select(Campaign).order_by(Campaign.id).offset(offset).limit(limit)).all() # type: ignore
    base_url=str(request.url).split('?')[0]
    print(base_url)
    next_url = f"{base_url}?offset={offset+limit}&limit={limit}"

    if offset > 0:
        #max will prevent us from calcualting a negative number, so offset will be zero if the compuation of the limit and offset is in nrgative
        prev_url = f"{base_url}?offset={max(0, offset-limit)}&limit={limit}"
    else:
        prev_url = None

    #returns pointers to the pevious and next urls
    return {
        "next":next_url,
        "prev":prev_url,
        "data":data
    }  # type: ignore



@app.get("/campaigns/{id}",response_model=Response[Campaign])
async def campaign(id:int,session:SessionDep):
  
    data=session.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    #wrap it in a dictionary
    return {"data":data}


#201 -> created successfully
@app.post("/campaigns",status_code=201,response_model=Response[Campaign])
# the endpoint excpects CampaignCreate
async def create_campaign(campaign:CampaignCreate,session:SessionDep):
    db_campaign=Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data":db_campaign}


@app.put("/campaigns/{id}",response_model=Response[Campaign])
async def update_campaign(id:int, campaign:CampaignCreate,session:SessionDep):
 data=session.get(Campaign,id)
 if not data:
    raise HTTPException(status_code=404)
 data.name=campaign.name
 data.due_date=campaign.due_date
 session.add(data)
 session.commit()
 session.refresh(data)
 #wrap it in a dictionary
 return {"data":data}


#204 -> deleted successfully
@app.delete("/campaigns/{id}",status_code=204)
async def delete_campaign(id:int,session:SessionDep):
    data=session.get(Campaign,id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()










# get all campagins 
# @app.get("/campaigns")
# async def read_campaigns():
#     return {"campaigns":data}

# # get campaign by id 
# @app.get("/campaigns/{id}")
# async def read_campaign(id:int):
#     for campaign in data:
#         if campaign.get("id")==id:
#             return {"campaign":campaign}
               
#     raise HTTPException(
#         status_code=404
#     )

# @app.post("/campaigns",status_code=201)
# async def create_campaign(body:dict[str,Any]): 
#     new:Any={
#         "id":randint(100,1000),
#         "name":body.get("name"),
#         "due_date": body.get("due_date"),
#         "created_at":datetime.now()  
#     }
#     data.append(new)
#     return {"campaign":new}

# @app.put("/campaigns/{id}")
# async def update_campaign(id:int, body:dict[str,Any]):
#     for index, campaign in enumerate(data):
#         if campaign.get("id")==id:
#             updated:Any={
            
#             }
#             data[index]=updated
#             return {"campaign":updated}
#     raise HTTPException(status_code=404)


# @app.delete("/campaign/{id}")
# async def delete_campaign(id:int):
#     for index, campaign in enumerate(data):
#         if campaign.get("id")==id:
#             data.pop(index)
#             return Response(status_code=204)
#     raise HTTPException(status_code=404)    