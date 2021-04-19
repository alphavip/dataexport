//
//  InfoMgr.h
//  GameSvr
//
//  Created by AlphaChen on 2016/10/24.
//
//

#include <stdint.h>
#include <map>
#include <unordered_map>

#ifndef _InfoMgr_H_
#define _InfoMgr_H_



namespace info
{

struct InfoHandle
{
    mutable int32_t index = -1;
    uint32_t infoId = 0;

    InfoHandle(int32_t i, uint32_t id) : index(i), infoId(id)
    {

    }
};
template <typename T>
class InfoMgr
{
private:
    InfoMgr(){}
    
public:
    virtual ~InfoMgr()
    {
        for(auto& t : this->m_infos)
            delete t;
    }
    
public:
    static inline InfoMgr &Get()
    {
        static InfoMgr obj;
        return obj;
    }
    static inline InfoMgr *GetPtr()
    {
        return &Get();
    }
    
public:
    int32_t Load(const base::CsvParser::Row& row)
    {
        T* t = new T();
        t->Load(row);
        this->Add(t);
        
        return 0;
    }
    const T* GetById(uint32_t id)
    {
        auto it = this->m_index.find(handle.infoId);
        if (it != this->m_index.end())
        {
            return this->m_infos[it->second];
        }

        return nullptr;

    }

    const T* GetByHandle(const InfoHandle& handle)
    {
        if(size_t(handle.index) < this->m_infos.size() && this->m_infos[handle.index]->id == handle.infoId)
            return this->m_infos[handle.index];
        auto it = this->m_index.find(handle.infoId);
        if (it != this->m_index.end())
        {
            handle.index = it->second;
            return this->m_infos[it->second];
        }
        return nullptr;
    }
    void Add(const T* t)
    {
        int32_t index = this->m_infos.size();
        this->m_infos.push_back(t);
        this->m_index[t->id] = index;
    }
    
public:
    void ForEach(std::function<int32_t (const T&)> f)
    {
        for(auto& t : this->m_infos)
        {
            if(f(*t) == 1)
                break;
        }
    }
    
    const std::vector<const T*>& GetAllInfo() const { return this->m_infos; }
    
protected:
    std::unordered_map<uint32_t, int32_t> m_index;//还是不用id作为vector下标了，如果id很随意，uint32_max个null还是很可观的
    std::vector<const T*> m_infos;//所有的配置
};
    
  
}


#endif // _InfoMgr_H_
